"""Build the add-on's copy of Vladimir from the main pack (Sanguine Pool at low health).

    python addons/league_vladimir_pool/make_override.py

Rebuilds Vladimir with tools/kit/build_vladimir.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_vladimir.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_vladimir_pool/override/league_vladimir.data_champion and .../text/champion.i18n: the same kit with
  * the main pack's danger check in his attack (two enemy champions on him, or hit at two checks in a row) left out;
  * passive = the add-on's league_vladimir_pool:guard with the numbers from P as its params (hp = n_hp, near =
    n_near, cost = n_cost): below hp% health with an enemy champion close it takes League's cost (cost% of his
    current health) and sets league_vladimir_w_go, and the data's own poll turns him into the pool;
  * the data's pool cost (w_cost% of max health, which took a 3% Vladimir to 1 health) is left out of the copy;
  * the attack's tooltip (the passive and the pool) points to description.league_vladimir_pool.attack with a "test
    build" lead and "below n_hp% health" for "in danger", so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Vladimir changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_vladimir_pool")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_vladimir as kit  # noqa: E402
import setup_vladimir as setup  # noqa: E402

MOD_ID = "league_vladimir_pool"
A, E = setup.A, setup.E
# lang -> (the lead, the main pack's words for the danger, the add-on's)
NATIVE = {
    "zh-hans": ("【残血血池测试版】", "危急时", "生命低于" + A + "{hp}%" + E + "时"),
    "zh-hant": ("【殘血血池測試版】", "危急時", "生命低於" + A + "{hp}%" + E + "時"),
    "en": ("[Low-health pool test build] ", "in danger", "below " + A + "{hp}%" + E + " health"),
    "ko": ("[빈사 웅덩이 테스트판] ", "위험할 때", "체력 " + A + "{hp}%" + E + " 미만일 때"),
    "ja": ("【瀕死の沼テスト版】", "危険時", "体力" + A + "{hp}%" + E + "未満で"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_vladimir.data_champion")), encoding="utf-8",
              newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_vladimir differs from build_vladimir.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != f"{MOD_ID}:guard":
        sys.exit("the native build has no league_vladimir_pool:guard passive: update this script")
    if "league_vladimir_sense" in json.dumps(champion["attack"]):
        sys.exit("the danger check is still in the attack: update this script")
    plain = kit.build(p, pay=False)          # the main pack's spells without the data's pool cost (the add-on pays it)
    if any(champion[k] != plain[k] for k in ("skill", "skill2", "ult")):
        sys.exit("the native build changes a spell beyond the pool's cost: update this script")
    if "league_vladimir_w_pay" in json.dumps(champion):
        sys.exit("the data's pool cost is still in the add-on's copy: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        main_text = setup.TEXT[lang]["attack"]
        if old not in main_text:
            sys.exit(f"{lang}: '{old}' is not in the main pack's attack text: update this script")
        texts[lang] = (lead + main_text.replace(old, new, 1)).format(hp=p["n_hp"], **values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_vladimir.data_champion")
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
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
