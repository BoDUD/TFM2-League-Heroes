"""Build the add-on's copy of Ekko from the main pack (Chronobreak back to 4 seconds ago, heal on the health lost).

    python addons/league_ekko_rewind/make_override.py [--check]

Reads the main pack's league/champion/league_ekko.data_champion, checks that src/lib.rs's numbers are the kit's (the
landing hit's ApAttack, its radius, R's range) and writes addons/league_ekko_rewind/override/league_ekko.data_champion
and .../text/champion.i18n: the same kit with -
  * R without its time anchor (the LinearProjectile league_ekko_r_anchor, the chrono / lives buffs, the hologram): the
    cast plays the departure picture and flags Ekko with lib.rs's GO; LAND_DELAY ticks later the main pack's landing
    (invulnerability, picture, sound, heal, the hit around him) runs without its Teleport;
  * the passive league_ekko_rewind:rewind (it moves him back and adds the heal bonus; the AI hook decides when R goes);
  * R's tooltip pointing to description.league_ekko_rewind.ult in the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Ekko changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ekko_rewind")
MOD_ID = "league_ekko_rewind"
HERO = "league_ekko"
TEXT_KEY = "description." + MOD_ID + ".ult"
PARAMS = {"base": 150, "ap": 80, "per": 4, "max": 200}
API = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
G, P, Y, E = "<#6aff55ff>", "<#a974ffff>", "<#ffb900ff>", "<>"
TEXT = {
    "zh-hans": "【附加包】回到" + Y + "4秒" + E + "前的位置，短暂无敌并回复" + G + "{b}" + E + " + " + API + P + "{a}% 法术强度" + E + "的" + G +
               "生命值" + E + "（这4秒每损失1%生命 +" + Y + "{per}%" + E + "，最多 +" + Y + "{top}%" + E + "），对落点周围的敌人造成" + P + "{d}" + E +
               " + " + API + P + "{da}% 法术强度" + E + "的" + P + "魔法伤害" + E + "。残血、掉血快或回去能打到人时释放。",
    "zh-hant": "【附加包】回到" + Y + "4秒" + E + "前的位置，短暫無敵並回復" + G + "{b}" + E + " + " + API + P + "{a}% 魔法強度" + E + "的" + G +
               "生命值" + E + "（這4秒每損失1%生命 +" + Y + "{per}%" + E + "，最多 +" + Y + "{top}%" + E + "），對落點周圍的敵人造成" + P + "{d}" + E +
               " + " + API + P + "{da}% 魔法強度" + E + "的" + P + "魔法傷害" + E + "。殘血、掉血快或回去能打到人時施放。",
    "en": "[Add-on] Ekko snaps back to where he was " + Y + "4s" + E + " ago, briefly invulnerable, heals " + G + "{b}" + E + " + " + API + P +
          "{a}% Ability Power" + E + " " + G + "health" + E + " (+" + Y + "{per}%" + E + " per 1% health lost in those 4s, up to +" + Y + "{top}%" + E +
          ") and deals " + P + "{d}" + E + " + " + API + P + "{da}% Ability Power" + E + " " + P + "magic damage" + E +
          " to enemies around his arrival point. Cast when low, after a burst, or to land on enemies.",
    "ko": "[확장] " + Y + "4초" + E + " 전의 위치로 되돌아갑니다. 잠시 무적이 되며 " + G + "체력" + E + "을 " + G + "{b}" + E + " + " + API + P + "주문력의 {a}%" + E +
          " 회복하고(그 4초 동안 잃은 체력 1%당 +" + Y + "{per}%" + E + ", 최대 +" + Y + "{top}%" + E + "), 도착 지점 주변의 적에게 " + P + "{d}" + E + " + " + API + P +
          "주문력의 {da}%" + E + " " + P + "마법 피해" + E + "를 입힙니다. 체력이 낮거나 급격히 잃었거나 적에게 착지할 수 있을 때 사용합니다.",
    "ja": "【拡張】" + Y + "4秒" + E + "前の位置へ戻る。一瞬無敵になり" + G + "体力" + E + "を" + G + "{b}" + E + " + " + API + P + "魔力の{a}%" + E +
          "回復し（その4秒の減少体力1%ごとに+" + Y + "{per}%" + E + "、最大+" + Y + "{top}%" + E + "）、到着地点周囲の敵に" + P + "{d}" + E + " + " + API + P +
          "魔力の{da}%" + E + "の" + P + "魔法ダメージ" + E + "を与える。瀕死、急な被弾、敵の中へ戻れる時に使う。",
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {}
    for name in ("LAND_DELAY", "R_BASE", "R_AP", "REWIND"):
        out[name] = int(re.search(r"pub const " + name + r": usize = ([\d_]+);", src).group(1).replace("_", ""))
    for name in ("LAND_R", "R_RANGE"):
        out[name] = int(re.search(r"pub const " + name + r": u64 = ([\d_]+);", src).group(1).replace("_", ""))
    out["GO"] = re.search(r'pub const GO: &str = "([^"]+)";', src).group(1)
    return out


def landing(ult):
    """The main pack's landing Combine (inside the anchor's Delayed, behind the lives / chrono checks)."""
    eff = ult["effect"]["effects"]
    anchor = [x for x in eff if x.get("type") == "LinearProjectile" and x.get("name") == "league_ekko_r_anchor"]
    if len(anchor) != 1:
        sys.exit("R's time anchor (league_ekko_r_anchor) changed: update this script")
    delayed = anchor[0]["end_effects"][0]
    lives = [x for x in delayed["effects"] if x.get("type") == "SwitchByBuff" and x.get("buff_name") == "league_ekko_lives"]
    chrono = lives[0]["effect_buff"] if lives else {}
    if chrono.get("buff_name") != "league_ekko_chrono" or delayed["tick"] + 1 != 240:
        sys.exit("R's rewind checks changed: update this script")
    return anchor[0], chrono["effect_buff"]


def build():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Ekko has a passive in the main pack now: update this script")
    u = champion["ult"]
    if u["casting_target"] != "EnemyChampion" or u["range"] != c["R_RANGE"]:
        sys.exit("R's casting target / range changed: update src/lib.rs's R_RANGE and the AI hook")
    anchor, land = landing(u)
    hits = [x for x in land["effects"] if x.get("type") == "RangeEffect" and x["target"] == "EnemyWithoutTower"
            and any(e.get("type") == "ApAttack" for e in x["effects"])]
    ap = [e for e in hits[0]["effects"] if e.get("type") == "ApAttack"] if len(hits) == 1 else []
    heal = [x for x in land["effects"] if x.get("type") == "Heal"]
    if (len(ap) != 1 or (ap[0]["damage"], ap[0]["attack_ratio"]) != (c["R_BASE"], c["R_AP"])
            or hits[0]["shape"]["Circle"]["radius"] != c["LAND_R"]):
        sys.exit("R's landing hit differs from src/lib.rs (R_BASE, R_AP, LAND_R): update one of them")
    if [(h["amount"], h["ap_ratio"]) for h in heal] != [(PARAMS["base"], PARAMS["ap"])]:
        sys.exit("R's heal changed: update PARAMS")
    keep = [x for x in land["effects"]
            if x.get("type") not in ("Teleport", "RemoveCasterBuff") and x.get("name") != "league_ekko_r_depart"]
    if len(keep) != len(land["effects"]) - 3:
        sys.exit("R's landing changed (Teleport / RemoveCasterBuff chrono / r_depart): update this script")
    cast = []
    for x in u["effect"]["effects"]:
        if x is anchor:
            cast += [{"type": "CasterViewEffect", "name": "league_ekko_r_depart"},
                     {"type": "AddCasterBuff", "buff_state": {"name": c["GO"], "duration": {"Time": {"tick": 3}}},
                      "only_to_enemy": False},
                     {"type": "Delayed", "tick": c["LAND_DELAY"], "effects": [{"type": "Combine", "effects": keep}]}]
        elif x.get("name") in ("league_ekko_r_ghost",) or x.get("buff_state", {}).get("name") == "league_ekko_chrono":
            continue
        else:
            cast.append(x)
    u["effect"]["effects"] = cast
    if "league_ekko_chrono" in json.dumps(champion) or "league_ekko_lives" in json.dumps(champion):
        sys.exit("the chrono / lives buffs are still used somewhere: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":rewind", "params": PARAMS}
    u["description"] = "#asset/base/text/champion?" + TEXT_KEY
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: TEXT[lang].format(b=PARAMS["base"], a=PARAMS["ap"], per=PARAMS["per"], top=PARAMS["max"],
                                     d=c["R_BASE"], da=c["R_AP"]) for lang in main_text}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
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
