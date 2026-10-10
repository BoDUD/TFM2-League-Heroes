"""Build the add-on's copy of Talon from the main pack (Assassin's Path over the map's walls).

    python addons/league_talon_vault/make_override.py

Rebuilds Talon with tools/kit/build_talon.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_talon.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_talon_vault/override/league_talon.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, its open-ground vault included (the way out where no wall is near);
  * passive = the add-on's league_talon_vault:path with the E numbers of P;
  * the e_wall buff picture (the vault's arc under him while the passive vaults him);
  * the attack's tooltip (it carries Assassin's Path) points to description.league_talon_vault.attack with the
    add-on's wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Talon changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_talon_vault")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_talon as kit  # noqa: E402
import setup_talon as setup  # noqa: E402

MOD_ID = "league_talon_vault"
HERO = "league_talon"
# lang -> (the lead, the main pack's Assassin's Path rule in the attack text, the add-on's)
NATIVE = {
    "zh-hans": ("【翻墙版】", "收刀或Q击杀时身边有{e_crowd}名敌方英雄，就翻身跃开并加速。",
                "被围或残血时翻墙撤离，残血敌人在墙后时翻墙追击；没墙时收刀或Q击杀被{e_crowd}人包围就跃开。之后加速。"),
    "zh-hant": ("【翻牆版】", "收刀或Q擊殺時身邊有{e_crowd}名敵方英雄，就翻身躍開並加速。",
                "被圍或殘血時翻牆撤離，殘血敵人在牆後時翻牆追擊；沒牆時收刀或Q擊殺被{e_crowd}人包圍就躍開。之後加速。"),
    "en": ("[Wall build] ",
           "when his blades return or his Q kills with {e_crowd} enemy champions near, he vaults away and runs faster.",
           "outnumbered or low, he vaults over a wall to escape, or onto a hurt champion behind one (no wall: away from "
           "{e_crowd} foes after W/Q), then runs faster."),
    "ko": ("[벽 넘기] ", "칼날이 돌아오거나 Q로 처치할 때 적 챔피언 {e_crowd}명이 가까이 있으면 뛰어올라 벗어나고 빨라집니다.",
           "포위·저체력이면 벽을 넘어 도주, 벽 뒤 약한 적은 넘어서 추격(벽이 없으면 W·Q 후 적 {e_crowd}명 근처에서 이탈). 이후 가속."),
    "ja": ("【壁越え】", "刃が戻る時かQで倒した時に敵チャンピオン{e_crowd}体が近いと跳んで離脱し加速。",
           "囲まれるか瀕死で壁を越えて離脱、壁裏の弱った敵へは壁越えで追撃（壁なしはW・Q後に敵{e_crowd}体で離脱）、加速。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_talon differs from build_talon.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":path":
        sys.exit("the copy has no league_talon_vault:path passive: update this script")
    if not any(v["name"] == HERO + "_e_wall" for v in champion["view_buffs"]):
        sys.exit("the copy has no e_wall picture: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        t = setup.TEXT[lang]["attack"]
        if t.count(old) != 1:
            sys.exit(f"{lang} attack: the main pack's text changed ({old!r} not found once): update NATIVE")
        texts[lang] = {"attack": (lead + t.replace(old, new)).format(**values)}
    long = {f"{lang}.attack": setup.shown_length(d["attack"]) for lang, d in texts.items()
            if setup.shown_length(d["attack"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.attack": f"{setup.shown_length(d['attack'])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items()})


if __name__ == "__main__":
    main()
