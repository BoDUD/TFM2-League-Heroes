"""Build the add-on's copy of Sylas from the main pack (Hijack by the robbed champion's class, Kingslayer by missing health,
the combos) and its class table.

    python addons/league_sylas/make_override.py [--game <Teamfight Manager2 folder>]

Rebuilds Sylas with tools/kit/build_sylas.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_sylas.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
  * addons/league_sylas/override/league_sylas.data_champion: the build with native - the main pack's kit, but
    Kingslayer's heal calls league_sylas:kingslayer, R's chain marks the champion it hits (league_sylas_r_mark), the
    second R plays the robbed League champion's own ult (league_sylas_steal_<hero>: every main-pack champion's ult
    effect tree as written, its animation tags turned into Sylas's ult_cast / ult_dash, the views it uses copied from
    that champion's lists; BY_CLASS lists the ones whose ult does nothing in his hands) or, for anyone else, one of
    five stolen ults by league_sylas_cls_<class>; passive
    league_sylas:hijack (params from P);
    the attack's and the ult's tooltips point to description.league_sylas_addon.* (so the tooltip in game shows
    whether the override took);
  * addons/league_sylas/text/champion.i18n: those two texts in five languages;
  * addons/league_sylas/src/classes.rs: champion id -> class for every base champion and every hero of this pack
    (league_viego_soul's table: the game's champion sheet's category, Melee / Range / Magician / Util / Assassin);
  * addons/league_sylas/src/stealable.rs: the League champions whose own ult the copy carries.
Every other champion stays untouched. Run it again whenever the main pack's Sylas changes or heroes are added.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_sylas")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "addons", "league_viego_soul"))
import build_sylas as kit  # noqa: E402
import setup_sylas as setup  # noqa: E402

TEXT_ID = "league_sylas_addon"      # the text's key (the hero's own id is league_sylas)
HERO = "league_sylas"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, M, A, R, G, E = setup.O, setup.M, setup.A, setup.R, setup.G, setup.E
mag, hl = setup.mag, setup.hl
# the ult's whole text in the add-on (the stolen ult by class)
ULT = {
    "zh-hans": "锁链命中敌方英雄，" + R + "眩晕" + E + A + "{r_stun}秒" + E + "并夺走大招；" + A + "{r_keep}秒" + E + "内再放：英雄联盟英雄放出他自己的大招（攻击加成按法强换算），"
               "其他英雄按类别放出" + mag("r2_dmg", "r2_ratio") + "魔法伤害的大招。",
    "zh-hant": "鎖鍊命中敵方英雄，" + R + "暈眩" + E + A + "{r_stun}秒" + E + "並奪走大招；" + A + "{r_keep}秒" + E + "內再放：英雄聯盟英雄放出他自己的大招（攻擊加成按法強換算），"
               "其他英雄按類別放出" + mag("r2_dmg", "r2_ratio") + "魔法傷害的大招。",
    "en": "His chain hits an enemy champion, " + R + "stuns" + E + " it for " + A + "{r_stun}s" + E + " and steals its ultimate; cast again "
          "within " + A + "{r_keep}s" + E + ": a League champion's own ultimate (its attack ratios paid from his ability power), "
          "any other champion's one by its class for " + mag("r2_dmg", "r2_ratio") + " magic damage.",
    "ko": "사슬이 적 챔피언을 맞혀 " + A + "{r_stun}초" + E + " " + R + "기절" + E + "시키고 궁극기를 빼앗음. " + A + "{r_keep}초" + E +
          " 안에 다시 쓰면 리그 오브 레전드 챔피언은 그 챔피언의 궁극기(공격력 계수는 주문력으로), 다른 챔피언은 계열별로 " +
          mag("r2_dmg", "r2_ratio") + " 마법 피해 궁극기.",
    "ja": "鎖が敵チャンピオンに当たると" + A + "{r_stun}秒" + E + R + "スタン" + E + "させアルティメットを奪う。" + A + "{r_keep}秒" + E +
          "以内に再使用：LoLのチャンピオンはその本人のアルティメット（攻撃力の係数は魔力で）、他はクラス別に" + mag("r2_dmg", "r2_ratio") +
          "の魔法ダメージ。",
}
# Kingslayer's heal grows with missing health: the attack's text with that ending
W_TAIL = {
    "zh-hans": ("回复" + hl("w_heal", "w_heal_r") + "生命。", "按损失生命多回" + hl("w_heal", "w_heal_r") + "起。"),
    "zh-hant": ("回復" + hl("w_heal", "w_heal_r") + "生命。", "按損失生命多回" + hl("w_heal", "w_heal_r") + "起。"),
    "en": ("healing " + hl("w_heal", "w_heal_r") + ".", "healing " + hl("w_heal", "w_heal_r") + ", more when hurt."),
    "ko": ("체력 " + hl("w_heal", "w_heal_r") + " 회복.", "체력 " + hl("w_heal", "w_heal_r") + "+ 회복(잃은 체력 비례)."),
    "ja": ("体力" + hl("w_heal", "w_heal_r") + "回復。", "体力" + hl("w_heal", "w_heal_r") + "～回復。"),
}

# what the add-on's attack text leaves out to fit with its lead (the details panel's limit, setup_sylas.TOOLTIP_MAX)
CUT = {
    "zh-hans": [("甩链。", ""), ("（最多2层）", "")],
    "zh-hant": [("甩鍊。", ""), ("（最多2層）", "")],
    "en": [("A chain swing. ", ""), (" (2 at most)", "")],
    "ko": [("사슬 휘두르기. ", ""), ("(최대 2)", "")],
    "ja": [("鎖を振るう。", ""), ("（最大2）", "")],
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


# League champions whose own ult does nothing in Sylas's hands, stolen by class instead (tools/kit/sylas_steal_check.py:
# a traced classic-engine game per champion with its ult stolen, 2026-10-20 - these showed none of their own pictures,
# projectiles or hits): their R slot only arms a flag that their own attacks / watchers fire, or it needs a state only
# they have
BY_CLASS = {
    "cassiopeia": "R arms a gaze her attacks fire", "evelynn": "R arms her next attacks", "gangplank": "R arms a barrage",
    "kayle": "R arms a save her watcher fires", "kindred": "R arms a save her watcher fires",
    "lillia": "R arms a sleep her attacks fire", "lissandra": "R arms a self-freeze her watcher fires",
    "samira": "R arms at S rank (her style grade)", "tahmkench": "R arms a devour his watcher fires",
    "tryndamere": "R arms undying his watcher fires", "urgot": "R arms an execute his attacks fire",
    "wukong": "R arms a spin his attacks fire", "zilean": "R arms a rewind his watcher fires",
    "gnar": "R only in Mega form", "orianna": "R needs her ball", "mel": "R strikes only her own Overwhelm stacks",
    "velkoz": "R casts only while his passive researches a champion",
    "shyvana": "R only at full Fury or in dragon form",
}


# a robbed champion's own animation tags -> Sylas's (his sheet has none of theirs): a dash, a leap or a flight his leap,
# anything else his stolen ult's cast
DASH_WORDS = ("dash", "leap", "jump", "fly", "air", "hop")


def sylas_tag(tag):
    return "ult_dash" if any(w in tag.lower() for w in DASH_WORDS) else "ult_cast"


def names_in(o, out):
    """Every name a tree uses for a picture, a projectile, a buff or a sound."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("name", "buff_name", "end_effect_name", "lock_effect_name", "range_effect_name") and isinstance(v, str):
                out.add(v)
            else:
                names_in(v, out)
    elif isinstance(o, list):
        for v in o:
            names_in(v, out)
    return out


def retag(o):
    """The tree with its CasterAnimation / RemoveCasterAnimation tags turned into Sylas's (sylas_tag)."""
    if isinstance(o, dict):
        o = {k: retag(v) for k, v in o.items()}
        if o.get("type") in ("CasterAnimation", "RemoveCasterAnimation"):
            o["name"] = sylas_tag(o["name"])
        return o
    if isinstance(o, list):
        return [retag(v) for v in o]
    return o


def own_ults():
    """[(hero without league_, ult effect retagged)] for every League champion of the main pack but Sylas, and the
    views those trees use, copied from each champion's own lists (their names carry the champion's id)."""
    stolen, views = [], {"view_projectiles": [], "view_effects": [], "view_buffs": []}
    seen = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "league", "champion", "league_*.data_champion"))):
        c = json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))
        if c["id"] == HERO or c["id"][len("league_"):] in BY_CLASS:
            continue
        tree = retag(c["ult"]["effect"])
        used = names_in(tree, set())
        for kind in views:
            for v in c.get(kind, []):
                if v["name"] in used and v["name"] not in seen:
                    seen.add(v["name"])
                    views[kind].append(v)
        stolen.append((c["id"][len("league_"):], tree))
    return stolen, views


def stealable_rs(stolen):
    lines = ["//! The League champions whose own ult the add-on's copy of Sylas carries (`league_sylas_steal_<hero>`), sorted.",
             "//! Generated by make_override.py from league/champion/*.data_champion - do not edit by hand.", "",
             "pub const STEALABLE: &[&str] = &["]
    lines += [f'    "league_{sid}",' for sid, _ in sorted(stolen)]
    lines.append("];")
    return chr(10).join(lines) + chr(10)


def classes_rs(table):
    lines = ["//! Every champion's class for the stolen ult: id -> melee / range / mage / util / assassin.",
             "//! Generated by make_override.py from the base game's champion sheet and this pack's heroes (league_viego_soul's",
             "//! table) - do not edit by hand.", "",
             "pub const CLASSES_OF: &[(&str, &str)] = &["]
    for cid, cat in table.items():
        lines.append(f'    ("{cid}", "{cat}"),')
    lines.append("];")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", help="Teamfight Manager2 folder (default: the usual Steam paths)")
    a = ap.parse_args()
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_sylas differs from build_sylas.P: rebuild it first")
    stolen, own_views = own_ults()
    champion = kit.build(p, native=True, own=stolen)
    for kind, vs in own_views.items():
        mine = {v["name"] for v in champion[kind]}
        clash = mine & {v["name"] for v in vs}
        if clash:
            sys.exit(f"view names in both Sylas and a robbed champion: {sorted(clash)}")
        champion[kind] += vs
    if champion.get("passive", {}).get("passive_ref") != "league_sylas:hijack":
        sys.exit("the copy does not call the add-on: update this script")
    text = json.dumps(champion)
    for name in ("league_sylas_r_mark", "league_sylas_cls_melee", "league_sylas_cls_assassin", "league_sylas:kingslayer",
                 "league_sylas_r_have", "league_sylas_w_cd", "league_sylas_r_real", "league_sylas_r_power_go",
                 "league_sylas_steal_jinx"):
        if name not in text:
            sys.exit(f"{name} is gone from the copy: update src/")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"

    v = setup.values(p)
    v["w_miss"] = p["w_miss"]
    texts, long = {}, {}
    for lang in LEAD:
        old, new = W_TAIL[lang]
        attack = setup.TEXT[lang]["attack"]
        if old not in attack:
            sys.exit(f"{lang}: the attack's text no longer ends with Kingslayer's heal - update W_TAIL")
        for a_, b_ in CUT.get(lang, ()):
            attack = attack.replace(a_, b_)
        attack = LEAD[lang] + attack.replace(old, new)
        ult = LEAD[lang] + ULT[lang]
        texts[lang] = {"attack": attack.format(**v), "ult": ult.format(**v)}
        for k, t in (("attack", attack), ("ult", ult)):
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6):
                long[f"{lang}.{k}"] = setup.shown_length(t)
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    import make_override as viego   # league_viego_soul's: the champion sheet's categories
    table = {cid: cat for cid, (cat, _) in viego.souls(a.game).items()}

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        # compact: the copy carries every League champion's ult (12 MB pretty-printed, 2.2 MB like this)
        f.write(json.dumps(champion, ensure_ascii=False, separators=(",", ":")) + "\n")
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    with open(lp(os.path.join(ADDON, "src", "classes.rs")), "w", encoding="utf-8", newline="\n") as f:
        f.write(classes_rs(table))
    with open(lp(os.path.join(ADDON, "src", "stealable.rs")), "w", encoding="utf-8", newline="\n") as f:
        f.write(stealable_rs(stolen))
    print(out)
    print(tpath)
    print("src/classes.rs -", len(table), "champions; src/stealable.rs -", len(stolen), "own ults;",
          sum(len(v) for v in own_views.values()), "views copied;", os.path.getsize(lp(out)) // 1024, "KB")


if __name__ == "__main__":
    main()
