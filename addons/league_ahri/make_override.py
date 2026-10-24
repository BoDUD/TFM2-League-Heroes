"""Build the add-on's copy of Ahri from the main pack (Essence Theft on every kill and takedown).

    python addons/league_ahri/make_override.py [--check]

Reads the main pack's league/champion/league_ahri.data_champion (tools/fix/ahri_league.py's kit) and writes
addons/league_ahri/override/league_ahri.data_champion and .../text/champion.i18n:
  * everything of the main pack's kit, the watchers on her actions included (they reward the flags tk_go / k_go);
  * no kill check on her attack and no takedown-window marks on her hits (the passive counts every kill and assist
    natively and raises the flags itself);
  * passive = the add-on's league_ahri:essence;
  * the attack's tooltip (it carries Essence Theft) in the add-on's wording, so the tooltip in game shows whether the
    override took.
Every other champion stays untouched. Run it again whenever the main pack's Ahri changes (--check: compare only).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ahri")
sys.path.insert(0, os.path.join(ROOT, "tools", "fix"))
import ahri_league as K  # noqa: E402
import ahri_league_text as T  # noqa: E402

MOD_ID = HERO = "league_ahri"
N = K.N
PARAMS = {"k_need": 9, "k_show": 6, "go": K.GO}


def lp(path):
    return K.lp(path)


def is_mark(o):
    """A takedown-window mark (ahri_league.mark): its first effect is the champion's p_alive keeper."""
    if not isinstance(o, dict) or o.get("type") != "Combine" or not o["effects"]:
        return False
    first = o["effects"][0]
    return first.get("type") == "AddCasted" and N + "p_alive" in json.dumps(first)


def is_twin(o):
    return isinstance(o, dict) and o.get("name") in (N + "kill_check", N + "mark") and "Projectile" in o.get("type", "")


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items()}
    if isinstance(o, list):
        return [strip(v) for v in o if not (is_mark(v) or is_twin(v))]
    return o


def build():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        main = json.load(f)
    if not K.done(main):
        sys.exit("the main pack's league_ahri is not tools/fix/ahri_league.py's kit yet")
    champion = strip(main)
    s = json.dumps(champion)
    for gone in ("p_alive", "kill_check", N + "mark\""):
        if gone in s:
            sys.exit(f"the copy still carries {gone}: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":essence", "params": PARAMS}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {"attack": T.attack(lang, K.P, addon=True)} for lang in main_text}
    long = {lang: T.shown_length(t["attack"]) for lang, t in texts.items()
            if T.shown_length(t["attack"]) > T.TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    return champion, {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    champion, text = build()
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps(text, ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(lp(p)) or open(lp(p), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print("league_ahri:", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files), "- passive =", champion["passive"]["passive_ref"],
          json.dumps(PARAMS))


if __name__ == "__main__":
    main()
