"""Build the add-on's copy of Annie from the main pack (Disintegrate refunds on a kill, Tibbers goes on to the next one).

    python addons/league_annie_q/make_override.py [--check]

Reads the main pack's league/champion/league_annie.data_champion and writes
addons/league_annie_q/override/league_annie.data_champion and .../text/champion.i18n: the same kit with -
  * both Q fireballs (TargetProjectile league_annie_q, 70 + 65% AP) calling the native effect league_annie_q:refund after
    their damage (it cuts Q's cooldown when the one struck died);
  * R keeping its summon (drop, hit, stun) but not Tibbers' follow: the Fire casted on the target and the 15 Delayed
    swipes / alive checks / vanish go; R marks its target with src/lib.rs's TIB_MARK instead, and the passive
    league_annie_q:tibbers runs Tibbers (the same pictures and numbers, checked here) and moves him on when the target dies;
  * Q's and R's tooltips pointing to description.league_annie_q.<slot>, one sentence added / swapped.
Every other champion stays untouched. Run it again whenever the main pack's Annie changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_annie_q")
MOD_ID = "league_annie_q"
HERO = "league_annie"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "skill": {
        "zh-hans": ("的<#a974ffff>魔法伤害<>。", "的<#a974ffff>魔法伤害<>。击杀目标时返还一半冷却。"),
        "zh-hant": ("的<#a974ffff>魔法傷害<>。", "的<#a974ffff>魔法傷害<>。擊殺目標時返還一半冷卻。"),
        "en": ("<#a974ffff>magic damage<>.", "<#a974ffff>magic damage<>. A kill refunds half its cooldown."),
        "ko": ("<#a974ffff>마법 피해<>를 입힙니다.", "<#a974ffff>마법 피해<>를 입힙니다. 대상을 처치하면 재사용 대기시간 절반을 돌려받습니다."),
        "ja": ("<#a974ffff>魔法ダメージ<>を与える。", "<#a974ffff>魔法ダメージ<>を与える。倒すとCDが半分戻る。"),
    },
    "ult": {
        "zh-hans": ("该英雄阵亡时提伯斯随之离场。", "该英雄阵亡时提伯斯转向附近的敌方英雄。"),
        "zh-hant": ("該英雄陣亡時泰貝爾隨之離場。", "該英雄陣亡時泰貝爾轉向附近的敵方英雄。"),
        "en": ("he leaves when the champion dies.", "when the champion dies he goes on to a nearby one."),
        "ko": ("그 챔피언이 죽으면 티버도 사라집니다.", "그 챔피언이 죽으면 티버는 근처의 다른 챔피언에게 갑니다."),
        "ja": ("そのチャンピオンが倒れるとティバーズも去る。", "そのチャンピオンが倒れるとティバーズは近くの別の敵へ向かう。"),
    },
}


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


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
    for k in ("TIB_LIFE", "TIB_FIRST", "TIB_PERIOD", "TIB_BURN", "TIB_BURN_AP"):
        out[k] = int(re.search(r"pub const " + k + r": usize = ([\d_]+);", src).group(1).replace("_", ""))
    out["TIB_R"] = int(re.search(r"pub const TIB_R: f64 = ([\d_]+)\.0;", src).group(1).replace("_", ""))
    out["TIB_MARK"] = re.search(r'pub const TIB_MARK: &str = "([^"]+)";', src).group(1)
    return out


def tibbers(ult, c):
    """R without Tibbers' follow; its numbers checked against src/lib.rs."""
    eff = ult["effect"]["effects"]
    loop = [x for x in eff if x.get("type") == "Delayed" and "league_annie_tibbers" in json.dumps(x)
            and '"casted_type": "Fire"' in json.dumps(x)]
    if len(loop) != 1:
        sys.exit("Tibbers' follow loop changed in the main pack: update this script")
    casted = loop[0]["effects"][0]
    burn = re.search(r'"name": "league_annie_r_burn", "shape": \{"Circle": \{"radius": (\d+)\}\}.*?"damage": (\d+), "attack_ratio": (\d+)',
                     json.dumps(casted))
    got = {"TIB_FIRST": loop[0]["tick"], "TIB_PERIOD": casted["period"], "TIB_R": int(burn.group(1)),
           "TIB_BURN": int(burn.group(2)), "TIB_BURN_AP": int(burn.group(3))}
    wrong = {k: (c[k], v) for k, v in got.items() if c[k] != v}
    if wrong:
        sys.exit(f"Tibbers differs from src/lib.rs (lib, kit): {wrong}")

    def drop(x):
        s = json.dumps(x)
        if x.get("type") == "AddCasted" and x.get("casted_type") == "Fire":
            return True  # the vanish at the end on the target
        return x.get("type") == "Delayed" and any(k in s for k in ("league_annie_tib_alive", "league_annie_tibbers\"",
                                                                    "league_annie_r_burn"))
    kept = [x for x in eff if not drop(x)]
    if len(eff) - len(kept) != 16:
        sys.exit(f"R dropped {len(eff) - len(kept)} pieces, not 16: update this script")
    mark = {"type": "AddBuff", "buff_state": {"name": c["TIB_MARK"], "duration": {"Time": {"tick": 3 + c["TIB_FIRST"]}}}}
    ult["effect"]["effects"] = kept + [mark]


def build():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Annie has a passive in the main pack now: update this script")
    call = {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":refund"}}

    def is_ball(o):
        return o.get("type") == "TargetProjectile" and o.get("name") == "league_annie_q"

    def add(o):
        hits = [a["effect"] for a in o["applied_effects"] if a["effect"].get("type") == "ApAttack"]
        if [(h["damage"], h["attack_ratio"]) for h in hits] != [(70, 65)]:
            sys.exit("Annie's Q damage changed: update this script")
        return dict(o, applied_effects=o["applied_effects"] + [call])

    n = []
    champion["skill"] = replace(champion["skill"], is_ball, add, n)
    if len(n) != 2 or champion["skill"]["cooltime"] != 240:
        sys.exit(f"Annie's Q ({len(n)} fireballs, cooldown {champion['skill']['cooltime']}) changed: update src/lib.rs's REFUND")
    tibbers(champion["ult"], c)
    champion["passive"] = {"passive_ref": MOD_ID + ":tibbers", "params": {}}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {lang: {"description": {MOD_ID: {}}} for lang in main_text}
    for slot, swaps in SWAPS.items():
        champion[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{slot}"
        for lang, tab in main_text.items():
            old, new = swaps[lang]
            t = tab["description"][HERO][slot]
            if old not in t:
                sys.exit(f"{lang} {HERO}.{slot}: the main pack's text changed ({old!r} not found): update this script")
            t = LEAD[lang] + t.replace(old, new)
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            text[lang]["description"][MOD_ID][slot] = t
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
