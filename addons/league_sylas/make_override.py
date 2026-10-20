"""Build the add-on's copy of Sylas from the main pack (Hijack by the robbed champion's class, Kingslayer by missing health,
the combos) and its class table.

    python addons/league_sylas/make_override.py [--game <Teamfight Manager2 folder>]

Rebuilds Sylas with tools/kit/build_sylas.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_sylas.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
  * addons/league_sylas/override/league_sylas.data_champion: the build with native - the main pack's kit, but
    Kingslayer's heal calls league_sylas:kingslayer, R's chain marks the champion it hits (league_sylas_r_mark), the
    second R picks one of five stolen ults by league_sylas_cls_<class>, passive league_sylas:hijack (params from P);
    the attack's and the ult's tooltips point to description.league_sylas_addon.* (so the tooltip in game shows
    whether the override took);
  * addons/league_sylas/text/champion.i18n: those two texts in five languages;
  * addons/league_sylas/src/classes.rs: champion id -> class for every base champion and every hero of this pack
    (league_viego_soul's table: the game's champion sheet's category, Melee / Range / Magician / Util / Assassin).
Every other champion stays untouched. Run it again whenever the main pack's Sylas changes or heroes are added.
"""
import argparse
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
    "zh-hans": "锁链命中敌方英雄，" + R + "眩晕" + E + A + "{r_stun}秒" + E + "并夺走大招；" + A + "{r_keep}秒" + E + "内再放，按对方类别放出" +
               mag("r2_dmg", "r2_ratio") + "魔法伤害的大招：近战跃起砸晕，射手贯穿长箭，法师爆发击飞，辅助治疗护盾友军，刺客闪身重击。",
    "zh-hant": "鎖鍊命中敵方英雄，" + R + "暈眩" + E + A + "{r_stun}秒" + E + "並奪走大招；" + A + "{r_keep}秒" + E + "內再放，按對方類別放出" +
               mag("r2_dmg", "r2_ratio") + "魔法傷害的大招：近戰躍起砸暈，射手貫穿長箭，法師爆發擊飛，輔助治療護盾友軍，刺客閃身重擊。",
    "en": "His chain hits an enemy champion, " + R + "stuns" + E + " it for " + A + "{r_stun}s" + E + " and steals its ultimate; cast again "
          "within " + A + "{r_keep}s" + E + " for one by its class, " + mag("r2_dmg", "r2_ratio") + " magic damage: a stunning leap "
          "(melee), a piercing arrow (marksman), a blast that knocks up (mage), heals and shields for allies (support), a blink and a "
          "heavy strike (assassin).",
    "ko": "사슬이 적 챔피언을 맞혀 " + A + "{r_stun}초" + E + " " + R + "기절" + E + "시키고 궁극기를 빼앗음. " + A + "{r_keep}초" + E +
          " 안에 다시 쓰면 상대 계열에 따라 " + mag("r2_dmg", "r2_ratio") + " 마법 피해: 근접 도약 기절, 원거리 관통 화살, 마법사 폭발 띄움, "
          "서포터 아군 회복·보호막, 암살자 순간이동 일격.",
    "ja": "鎖が敵チャンピオンに当たると" + A + "{r_stun}秒" + E + R + "スタン" + E + "させアルティメットを奪う。" + A + "{r_keep}秒" + E +
          "以内に再使用で相手のクラス別に" + mag("r2_dmg", "r2_ratio") + "の魔法ダメージ：近接は跳躍スタン、射手は貫通矢、魔術師は爆発、"
          "サポートは味方回復とシールド、暗殺者は瞬間移動の一撃。",
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
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != "league_sylas:hijack":
        sys.exit("the copy does not call the add-on: update this script")
    text = json.dumps(champion)
    for name in ("league_sylas_r_mark", "league_sylas_cls_melee", "league_sylas_cls_assassin", "league_sylas:kingslayer",
                 "league_sylas_r_have", "league_sylas_w_cd"):
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
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    with open(lp(os.path.join(ADDON, "src", "classes.rs")), "w", encoding="utf-8", newline="\n") as f:
        f.write(classes_rs(table))
    print(out)
    print(tpath)
    print("src/classes.rs -", len(table), "champions")


if __name__ == "__main__":
    main()
