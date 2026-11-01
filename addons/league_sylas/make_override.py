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
  * addons/league_sylas/src/stealable.rs: the champions whose own ult the copy carries;
  * addons/league_sylas/effects/: the effect sheets a TFT hero's stolen ult draws (copies of tft/effects), so the copy
    never points into the tft mod - the add-on bundle is on the Workshop and the tft mod is not, and a view whose
    sheet is missing breaks the game when the champion is picked (league_swain, 2026-10-25), not when it is played.
The TFT heroes (tft/champion, 2026-10-26: 「塞拉斯不会偷拉露恩、诺拉、爆爆？」) are robbed like the League ones: their own
ult when it is plain data that works in his hands, else BY_CLASS. Every other champion stays untouched. Run it again whenever the main pack's Sylas changes or heroes are added.
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
import generated  # noqa: E402  --check

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
    # the TFT heroes (tft/champion): their code is tft.dll's, not the add-on bundle's
    "tft_alune": "R's moon reads her phases and her passive's code splits it",
    "tft_norra": "R's rift is tft.dll's own code (a native the tft mod registers)",
    "shyvana": "R only at full Fury or in dragon form", "heimerdinger": "R arms an upgrade his next spell fires",
}


# TFT heroes whose own ult is tft.dll's code (a Native): their kit builds a plain-data version for Sylas (module,
# function -> the ult's effect tree; its views are the hero's own lists), so his stolen ult still shows their effects
# (the user, 2026-10-27: 「塞拉斯的大招什么一定要能偷到特效版本的」)
STOLEN = {"tft_silco": ("build_silco", "sylas_ult"), "tft_maddie": ("build_maddie", "sylas_ult"),
          "tft_vander": ("build_vander", "sylas_ult"), "tft_violet": ("build_violet", "sylas_ult"),
          "tft_renni": ("build_renni", "sylas_ult"),
          "tft_smeech": ("build_smeech", "sylas_ult"),
          "tft_sevika": ("build_sevika", "sylas_ult"),
          "tft_steb": ("build_steb", "sylas_ult"),
          "tft_daeja": ("build_daeja", "sylas_ult"),
          "tft_syfen": ("build_syfen", "sylas_ult"),
          "tft_sohm": ("build_sohm", "sylas_ult"),
          "tft_terra": ("build_terra", "sylas_ult"),
          "tft_zippy": ("build_zippy", "sylas_ult"),

          "tft_sentinel": ("build_sentinel", "sylas_ult"),
          "tft_raptor": ("build_raptor", "sylas_ult"),
          "tft_elderdragon": ("build_elderdragon", "sylas_ult"),
          "tft_meepsie": ("build_meepsie", "sylas_ult"),
          "tft_murkwolf": ("build_murkwolf", "sylas_ult")}


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


def no_lasting_reach(o):
    """The tree with the attack range taken off every Permanent buff it lays (game 0.7.0 audit): a form's or a state's
    reach belongs to its owner's kit, which takes it off again (league_jayce's cannon `cn` +25000 when he turns back,
    league_rengar's `ready` +25000, league_khazix's evolved `s1` +6000) - in Sylas's hands nothing ever did, so a stolen
    Jayce / Rengar / Kha'Zix R left him that reach until he died. 0.6.x's AI stood him off at it; 0.7.0 fixed the
    engine's stretched reach ("a champion whose attacks were changed by a mod ... moved back and forth"), so he would
    really chain from it. Timed range buffs (Twitch R, Akali, Seraphine's notes ...) end with the steal and are kept."""
    if isinstance(o, dict):
        o = {k: no_lasting_reach(v) for k, v in o.items()}
        st = o.get("buff_state")
        if o.get("type") in ("AddBuff", "AddCasterBuff") and isinstance(st, dict) and st.get("duration") == "Permanent"                 and (st.get("range") or 0) > 0:
            o["buff_state"] = {k: v for k, v in st.items() if k != "range"}
        return o
    if isinstance(o, list):
        return [no_lasting_reach(v) for v in o]
    return o


# a TFT hero's effect sheets: tft/effects/<sheet> -> the add-on's own copy (asset/league_sylas/effects/<sheet>)
TFT_FX = "asset/tft/effects/"
OWN_FX = "asset/league_sylas/effects/"


def key(cid):
    """The hero's name in steal_<name>: a League champion without league_, a TFT hero as it is (tft_powder)."""
    return cid[len("league_"):] if cid.startswith("league_") else cid


def full(sid):
    return sid if sid.startswith("tft_") else "league_" + sid


def own_ults():
    """[(key, ult effect retagged)] for every League champion of the main pack and every TFT hero but Sylas and BY_CLASS,
    the views those trees use, copied from each champion's own lists (their names carry the champion's id), and the
    TFT effect sheets they draw (their views point at the add-on's copies)."""
    stolen, views = [], {"view_projectiles": [], "view_effects": [], "view_buffs": []}
    seen, sheets = set(), set()
    paths = sorted(glob.glob(os.path.join(ROOT, "league", "champion", "league_*.data_champion")))
    paths += sorted(glob.glob(os.path.join(ROOT, "tft", "champion", "tft_*.data_champion")))
    for path in paths:
        c = json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))
        if c["id"] == HERO or key(c["id"]) in BY_CLASS:
            continue
        if c["id"] in STOLEN:
            import importlib
            mod, fn = STOLEN[c["id"]]
            tree = no_lasting_reach(retag(getattr(importlib.import_module(mod), fn)()))
        else:
            tree = no_lasting_reach(retag(c["ult"]["effect"]))
        if '"Native"' in json.dumps(tree):
            sys.exit(f"{c['id']}: its ult calls native code - put it in BY_CLASS or make the add-on carry it")
        used = names_in(tree, set())
        for kind in views:
            for v in c.get(kind, []):
                if v["name"] in used and v["name"] not in seen:
                    seen.add(v["name"])
                    anim = v.get("anim", "")
                    if anim.startswith(TFT_FX):
                        sheets.add(anim[len(TFT_FX):])
                        v = {**v, "anim": OWN_FX + anim[len(TFT_FX):]}
                    elif anim.startswith("asset/tft/"):
                        sys.exit(f"{c['id']}: view {v['name']} draws {anim} - only tft/effects sheets are copied")
                    views[kind].append(v)
        stolen.append((key(c["id"]), tree))
    return stolen, views, sheets


def sheet_files(sheets):
    """[(the add-on's copy, the tft mod's file)] for every TFT sheet the copy draws."""
    out = []
    for name in sorted(sheets):
        for ext in ("#anim.fanim", "#sheet.png"):
            out.append((os.path.join(ADDON, "effects", name + ext), os.path.join(ROOT, "tft", "effects", name + ext)))
    return out


def stealable_rs(stolen):
    lines = ["//! The League champions whose own ult the add-on's copy of Sylas carries (`league_sylas_steal_<hero>`), sorted.",
             "//! Generated by make_override.py from league/champion and tft/champion - do not edit by hand.", "",
             "pub const STEALABLE: &[&str] = &["]
    lines += [f'    "{cid}",' for cid in sorted(full(sid) for sid, _ in stolen)]
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
    ap.add_argument("--check", action="store_true",
                    help="CI: rebuild what does not need the game and fail if the committed files differ")
    a = ap.parse_args()
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_sylas differs from build_sylas.P: rebuild it first")
    stolen, own_views, sheets = own_ults()
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

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    # compact: the copy carries every League champion's ult (12 MB pretty-printed, 2.2 MB like this)
    copy_text = json.dumps(champion, ensure_ascii=False, separators=(",", ":")) + "\n"
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    spath = os.path.join(ADDON, "src", "stealable.rs")
    copies = sheet_files(sheets)
    if a.check:
        stale = [os.path.relpath(c, ROOT) for c, src in copies
                 if not os.path.isfile(lp(c)) or open(lp(c), "rb").read() != open(lp(src), "rb").read()]
        if stale:
            sys.exit("league_sylas: the TFT effect copies are out of date - run make_override.py and commit: "
                     + ", ".join(stale))
        generated.check("league_sylas", [(out, copy_text), (tpath, dumps_main(i18n)), (spath, stealable_rs(stolen))],
                        ["src/classes.rs"])
        return
    import make_override as viego   # league_viego_soul's: the champion sheet's categories
    table = {cid: cat for cid, (cat, _) in viego.souls(a.game).items()}

    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(copy_text)
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    with open(lp(os.path.join(ADDON, "src", "classes.rs")), "w", encoding="utf-8", newline="\n") as f:
        f.write(classes_rs(table))
    with open(lp(spath), "w", encoding="utf-8", newline="\n") as f:
        f.write(stealable_rs(stolen))
    for c, src in copies:
        os.makedirs(lp(os.path.dirname(c)), exist_ok=True)
        with open(lp(c), "wb") as f:
            f.write(open(lp(src), "rb").read())
    print(out)
    print(tpath)
    print("src/classes.rs -", len(table), "champions; src/stealable.rs -", len(stolen), "own ults;",
          sum(len(v) for v in own_views.values()), "views copied;", os.path.getsize(lp(out)) // 1024, "KB")


if __name__ == "__main__":
    main()
