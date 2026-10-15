"""Build the add-on's copy of Smolder from the main pack (stacks kept, the tier-3 execute, Flap over walls).

    python addons/league_smolder/make_override.py

Rebuilds Smolder with tools/kit/build_smolder.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_smolder.data_champion (so the copy never drifts from the shipped kit) and that src/lib.rs's
effect constants match P, and writes addons/league_smolder/override/league_smolder.data_champion and
.../text/champion.i18n: the build with native=1 -
  * skill2 is the sneeze only; the passive league_smolder:dragon flies Flap, Flap, Flap itself (when, where - over
    walls - and the shots) and keeps the stacks through death; the tier-3 breath calls league_smolder:execute;
  * the attack's (passive), skill's and skill2's tooltips point to description.league_smolder.* with the add-on's
    wording, so the tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Smolder changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_smolder")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_smolder as kit  # noqa: E402
import setup_smolder as setup  # noqa: E402

MOD_ID = "league_smolder"
HERO = "league_smolder"
# src/lib.rs constant -> P's number (the effects' numbers live in the DLL)
CONSTS = {"E_DMG": lambda p: p["e_dmg"], "E_RATIO": lambda p: p["e_ratio"], "E_STACK": lambda p: p["e_stack"],
          "E_EXEC": lambda p: p["e_exec"], "E_GOT_T": lambda p: p["e_anim"] + 20, "P_PEND": lambda p: p["p_pend"]}
A = setup.A
E = setup.E
# lang -> key -> [(the main pack's words, the add-on's)]
NATIVE = {
    "zh-hans": {
        "attack": [("（阵亡清空）", "（【附加包】死后保留）")],
        "skill": [("最大生命真实伤害" + E + "。", "最大生命真实伤害" + E + "；【附加包】生命低于" + A + "6.5%" + E + "的敌人被处决。")],
        "skill2": [("被近身或追击残血时改用", "【附加包】被近身或追残血时随时可用，能飞过墙：")],
    },
    "zh-hant": {
        "attack": [("（陣亡清空）", "（【擴充包】死後保留）")],
        "skill": [("最大生命真實傷害" + E + "。", "最大生命真實傷害" + E + "；【擴充包】生命低於" + A + "6.5%" + E + "的敵人被處決。")],
        "skill2": [("被近身或追擊殘血時改用", "【擴充包】被近身或追殘血時隨時可用，能飛過牆：")],
    },
    "en": {
        "attack": [("(lost on death)", "(kept through death: add-on)")],
        "skill": [(" a second.", " a second; [Add-on] enemies below " + A + "6.5%" + E + " health are executed.")],
        "skill2": [("When dived, or chasing a wounded enemy:", "[Add-on] Any time he is dived or chases a wounded foe, over walls too:")],
    },
    "ko": {
        "attack": [("(사망 시 소멸)", "([확장팩] 사망 후 유지)")],
        "skill": [(" 최대 체력 고정 피해" + E + ".", " 최대 체력 고정 피해" + E + ". [확장팩] 체력 " + A + "6.5%" + E + " 미만 적 처형.")],
        "skill2": [("적이 붙거나 약한 적을 쫓을 때는", "[확장팩] 적이 붙거나 약한 적을 쫓을 때 언제든, 벽 너머로도")],
    },
    "ja": {
        "attack": [("（死亡で消滅）", "（【拡張】死後も保持）")],
        "skill": [("最大体力の確定ダメージ" + E + "。", "最大体力の確定ダメージ" + E + "。【拡張】体力" + A + "6.5%" + E + "未満の敵は処刑。")],
        "skill2": [("詰められた時か弱った敵を追う時は", "【拡張】詰められた時か弱った敵を追う時、壁越しにも")],
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        shipped = json.load(f)
    if kit.build(p) != shipped:
        sys.exit("the main pack's league_smolder differs from build_smolder.P: rebuild it first")
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    for name, want in CONSTS.items():
        m = re.search(rf"pub const {name}: usize = ([\d_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != want(p):
            sys.exit(f"src/lib.rs {name} is not P's {want(p)}: update the constant")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":dragon":
        sys.exit("the copy has no league_smolder:dragon passive: update this script")
    keys = ("attack", "skill", "skill2")
    for k in keys:
        champion[k]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{k}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in NATIVE.items():
        texts[lang] = {}
        for k in keys:
            t = setup.TEXT[lang][k]
            for old, new in swaps[k]:
                if t.count(old) != 1:
                    sys.exit(f"{lang} {k}: the main pack's text changed ({old!r} not found once): update NATIVE")
                t = t.replace(old, new)
            texts[lang][k] = t.format(**values)
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in texts.items() for k, t in d.items()
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
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
