"""Build the add-on's copy of Brand from the main pack (Blaze stacks counted on each enemy champion).

    python addons/league_brand/make_override.py

Rebuilds Brand with tools/kit/build_brand.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_brand.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
add-on's constants (src/lib.rs B_KEEP, P_WAIT, P_DET_R, P_DET, P_DET_AP, P_DET_HP, P_T, P_PERIOD, P_BURN, P_BURN_AP)
are P's, and writes addons/league_brand/override/league_brand.data_champion and .../text/champion.i18n: the build with
native=1 -
  * every spell hit on an enemy champion: the stack climb on him (caster flags b_1 -> b_2) is the add-on's `Native`
    league_brand:blaze, which stacks on that champion and detonates it itself;
  * passive = the add-on's league_brand:watch (diagnostics: a SPAWN line when he spawns, a WATCH line every 30 s);
  * the attack's tooltip (the passive) points to description.league_brand.attack with a "test build" lead and the
    per-enemy, magic wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Brand changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_brand")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_brand as kit  # noqa: E402
import setup_brand as setup  # noqa: E402

MOD_ID = "league_brand"
M, W, E, mag = setup.M, setup.W, setup.E, setup.mag
DET = mag("p_det", "p_det_ap")
# lang -> (the lead, the main pack's stacking sentence, the add-on's: stacks on each champion, magic % max health)
NATIVE = {
    "zh-hans": ("【层数测试版】",
                "技能命中英雄叠层，第3层时该英雄{p_wait}秒后爆炸，对周围造成" + DET + "+" + W + "{p_det_hp}%最大生命值" + E + "伤害。",
                "技能命中的英雄各自叠层，第3层时他{p_wait}秒后爆炸，对周围造成" + DET + "+" + M + "{p_det_hp}%最大生命值魔法伤害" +
                E + "。"),
    "zh-hant": ("【層數測試版】",
                "技能命中英雄疊層，第3層時該英雄{p_wait}秒後爆炸，對周圍造成" + DET + "+" + W + "{p_det_hp}%最大生命值" + E + "傷害。",
                "技能命中的英雄各自疊層，第3層時他{p_wait}秒後爆炸，對周圍造成" + DET + "+" + M + "{p_det_hp}%最大生命值魔法傷害" +
                E + "。"),
    "en": ("[Stacks test build] ",
           "Spell hits on champions stack; at 3 stacks that champion detonates {p_wait}s later for " + DET + " + " + W +
           "{p_det_hp}% max health" + E + " damage round it.",
           "Spell hits stack on each champion they hit; at 3 stacks that champion detonates {p_wait}s later for " + DET +
           " + " + M + "{p_det_hp}% max health magic damage" + E + " round it."),
    "ko": ("[중첩 테스트판] ",
           "챔피언 적중 시 중첩, 3중첩 시 그 챔피언이 {p_wait}초 후 폭발해 주변에 " + DET + " + " + W + "최대 체력의 {p_det_hp}%" + E +
           " 피해.",
           "적중한 챔피언마다 따로 중첩, 3중첩 시 그 챔피언이 {p_wait}초 후 폭발해 주변에 " + DET + " + " + M +
           "최대 체력의 {p_det_hp}% 마법 피해" + E + "."),
    "ja": ("【スタックテスト版】",
           "チャンピオンへの命中でスタック、3スタックでそのチャンピオンが{p_wait}秒後に爆発し周囲に" + DET + "+" + W +
           "最大体力の{p_det_hp}%" + E + "のダメージ。",
           "命中したチャンピオンごとにスタック、3スタックでそのチャンピオンが{p_wait}秒後に爆発し周囲に" + DET + "+" + M +
           "最大体力の{p_det_hp}%の魔法ダメージ" + E + "。"),
}
CONSTS = {"B_KEEP": "b_keep", "P_WAIT": "p_wait", "P_DET_R": "p_det_r", "P_DET": "p_det", "P_DET_AP": "p_det_ap",
          "P_DET_HP": "p_det_hp", "P_T": "p_t", "P_PERIOD": "p_period", "P_BURN": "p_burn", "P_BURN_AP": "p_burn_ap"}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_const(name):
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        m = re.search(rf"pub const {name}: \w+ = ([\d_]+);", f.read())
    if not m:
        sys.exit(f"src/lib.rs has no const {name}")
    return int(m.group(1).replace("_", ""))


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_brand.data_champion")), encoding="utf-8",
              newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_brand differs from build_brand.P: rebuild it first")
    for const, key in CONSTS.items():
        if rust_const(const) != p[key]:
            sys.exit(f"src/lib.rs {const} = {rust_const(const)} but P[{key!r}] = {p[key]}: make them agree")
    if p["p_hp"]:
        sys.exit("P's p_hp is not 0: the add-on's burn has no max-health part, add it to src/lib.rs first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps({k: v for k, v in champion.items() if not k.startswith("view_")})   # the skill trees
    n = text.count(f'"effect_ref": "{MOD_ID}:blaze"')
    if not n or f'"{MOD_ID}_b_2"' in text or f'"{MOD_ID}_p_unstable"' in text:
        sys.exit("the copy still climbs b_2 / lays p_unstable itself, or has no league_brand:blaze: update this script")
    if "passive" in champion:
        sys.exit("the main pack's Brand has a passive now: update this script (the copy's is the watch)")
    champion["passive"] = {"passive_ref": f"{MOD_ID}:watch", "params": {}}   # diagnostics: SPAWN / WATCH lines
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        attack = setup.TEXT[lang]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update NATIVE")
        texts[lang] = (lead + attack.replace(old, new)).format(**values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_brand.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "-", n,
          "champion hits are league_brand:blaze")
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
