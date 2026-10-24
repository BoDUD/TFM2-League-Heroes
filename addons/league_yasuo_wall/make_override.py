"""Build the add-on's copy of Yasuo from the main pack (Wind Wall, raised by the add-on when missiles come).

    python addons/league_yasuo_wall/make_override.py [--check]

Reads the main pack's league/champion/league_yasuo.data_champion and writes
addons/league_yasuo_wall/override/league_yasuo.data_champion and .../text/champion.i18n: the same kit with -
  * the passive league_yasuo_wall:wall (Yasuo has no free slot: the add-on raises the wall itself);
  * view_effects for the wall's pictures (tools/art/import_yasuo_wall.py -> effects/league_yasuo_wall_fx): the PIECES
    upright pieces of wind league_yasuo_w_plume_<k> and the ground dot league_yasuo_w_ground, played at points on the
    ground (not following anyone, never turned);
  * the attack's tooltip (it carries his passive) pointing to description.league_yasuo_wall.attack, one sentence added.
Every other champion stays untouched. Run it again whenever the main pack's Yasuo changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yasuo_wall")
MOD_ID = "league_yasuo_wall"
HERO = "league_yasuo"
SLOT = "attack"
FX = "league_yasuo_wall_fx"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, O, E = "<#ffb900ff>", "<#ff9028ff>", "<>"
ADD = {
    "zh-hans": O + "风之障壁" + E + "：飞行物来袭时竖起风墙" + Y + "4秒" + E + "，挡下敌方英雄的飞行物（" + Y + "20秒" + E + "一次）。",
    "zh-hant": O + "風之障壁" + E + "：飛行物來襲時豎起風牆" + Y + "4秒" + E + "，擋下敵方英雄的飛行物（" + Y + "20秒" + E + "一次）。",
    "en": " " + O + "Wind Wall" + E + ": stops enemy champions' missiles for " + Y + "4s" + E + " when they fly in (every " + Y +
          "20s" + E + ").",
    "ko": " " + O + "바람 장막" + E + ": " + Y + "4초" + E + "간 적 챔피언 투사체 차단(" + Y + "20초" + E + "마다).",
    "ja": O + "風殺の壁" + E + "：" + Y + "4秒" + E + "敵の飛び道具を防ぐ（" + Y + "20秒" + E + "毎）。",
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    pieces = int(re.search(r"pub const PIECES: usize = (\d+);", src).group(1))
    piece = re.search(r'pub const PIECE_PIC: &str = "([^"]+)";', src).group(1)
    ground = re.search(r'pub const GROUND_PIC: &str = "([^"]+)";', src).group(1)
    anims = json.load(open(lp(os.path.join(ADDON, "effects", FX + "#anim.fanim")), encoding="utf-8-sig"))["anims"]
    want = [f"plume_{k}" for k in range(pieces)] + ["ground"]
    missing = [t for t in want if t not in anims]
    if missing:
        sys.exit(f"effects/{FX} lacks {missing}: run tools/art/import_yasuo_wall.py")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Yasuo has a passive in the main pack now: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":wall", "params": {}}
    anim = f"asset/{MOD_ID}/effects/{FX}"
    views = [{"type": "Animation", "name": f"{piece}{k}", "anim": anim, "tag": f"plume_{k}", "z": 1, "is_follow": False}
             for k in range(pieces)]
    views.append({"type": "Animation", "name": ground, "anim": anim, "tag": "ground", "z": -1, "is_follow": False})
    names = {v["name"] for v in champion["view_effects"]}
    if names & {v["name"] for v in views}:
        sys.exit("the main pack's Yasuo already has these view names: update this script")
    champion["view_effects"] = champion["view_effects"] + views
    champion[SLOT]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{SLOT}"
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {}
    for lang, tab in main_text.items():
        t = LEAD[lang] + tab["description"][HERO][SLOT] + ADD[lang]
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        text[lang] = {"description": {MOD_ID: {SLOT: t}}}
    return champion, text


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
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files))


if __name__ == "__main__":
    main()
