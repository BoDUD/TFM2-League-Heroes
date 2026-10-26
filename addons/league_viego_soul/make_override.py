"""Build the add-on's copy of Viego from the main pack, the soul table and the add-on's tooltip.

    python addons/league_viego_soul/make_override.py [--game <TFM2 folder>]

Rebuilds Viego with tools/kit/build_viego.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_viego.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes:
  * override/league_viego.data_champion: build(p) with native=1 - the passive league_viego_soul:possess (params from P),
    his hits on champions leave league_viego_mark on them instead of the data's takedown watch, the five soul kits
    (melee / range / mage / util / assassin) in his attack, Q and W behind SwitchByBuff league_viego_soul_<category>,
    the possession's pictures and sounds played on the add-on's flags league_viego_p_go / p_off;
  * text/champion.i18n: description.league_viego_soul.attack - the passive as the add-on plays it;
  * src/souls.rs: champion id -> (soul category, the animation tags of its sheet) for every base champion (the game's
    champion sheet asset/base/setting/champion_info and each sprite's #anim, bundle.game_data), every hero of this
    pack (league/champion + league/champions/*#anim.fanim) and of the repo's tft pack (tft/champion + tft/champions:
    the user, 2026-10-26: 「让佛耶戈和妮蔻也能变成 tft 英雄」). The view hook draws only champions in this table;
    league_neeko reads the same file for the allies she can disguise as.
Run it again whenever the main pack's Viego or his text changes, or when the pack gains heroes.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_viego_soul")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import build_viego as kit  # noqa: E402
import setup_viego as setup  # noqa: E402
import generated  # noqa: E402  --check

MOD_ID = "league_viego_soul"
HERO = "league_viego"
CATS = {"Melee": "melee", "Range": "range", "Magician": "mage", "Util": "util", "Assassin": "assassin"}
O, A, R, E = setup.O, setup.A, setup.R, setup.E
TEXT = {
    "zh-hans": O + "君命已决" + E + "（附加包）：他伤过的敌方英雄{p_win}秒内阵亡，尸体处留下灵魂{soul_t}秒，靠近即附身" + A + "{p_t}秒" + E +
               "：整个身体变成那个英雄，按其类别用近战 / 射手 / 法师 / 辅助 / 刺客的招式，" + R + "{p_inv}秒无敌" + E + "，攻击+{p_ad}%、攻速+{p_as}%，Q、W冷却减半。",
    "zh-hant": O + "王權統御" + E + "（擴充包）：他傷過的敵方英雄{p_win}秒內陣亡，屍體處留下靈魂{soul_t}秒，靠近即附身" + A + "{p_t}秒" + E +
               "：整個身體變成那個英雄，按其類別用近戰 / 射手 / 法師 / 輔助 / 刺客的招式，" + R + "{p_inv}秒無敵" + E + "，攻擊+{p_ad}%、攻速+{p_as}%，Q、W冷卻減半。",
    "en": O + "Sovereign's Domination" + E + " (add-on): an enemy champion he damaged dies within {p_win}s - its soul waits {soul_t}s; "
          "near it he possesses it for " + A + "{p_t}s" + E + ": he takes its whole body and fights with its class's moves (fighter, "
          "marksman, mage, support, assassin), " + R + "untouchable {p_inv}s" + E + ", +{p_ad}% attack, +{p_as}% attack speed, Q and W cooldowns halved.",
    "ko": O + "군주의 지배" + E + "(확장팩): 피해를 입힌 적 챔피언이 {p_win}초 안에 죽으면 영혼이 {soul_t}초 남고, 다가가면 " + A + "{p_t}초" + E +
          " 빙의: 그 챔피언의 몸이 되어 계열(전사·원거리·마법사·서포터·암살자)의 기술을 쓰고 " + R + "{p_inv}초 무적" + E + ", 공격력 +{p_ad}%, 공격 속도 +{p_as}%, Q·W 재사용 대기시간 절반.",
    "ja": O + "王の支配" + E + "（拡張）：ダメージを与えた敵チャンピオンが{p_win}秒以内に倒れると魂が{soul_t}秒残り、近づくと" + A + "{p_t}秒" + E +
          "憑依：その体になり系統（ファイター・射手・メイジ・サポート・アサシン）の技を使う。" + R + "{p_inv}秒無敵" + E + "、攻撃力+{p_ad}%・攻撃速度+{p_as}%、QとWのクールダウン半減。",
}

# W in the copy (0.2.0): the mist rises by itself near enemy champions, W is the maw alone - setup_viego's W text with
# its mist clause rewritten: (old, new) per language, each once in setup_viego.TEXT[lang]["skill2"]
W_SWAP = {
    "zh-hans": [("：黑雾升起，", "（附加包）：敌方英雄进到附近时黑雾自己升起（每{e_cd}秒最多一次），"),
                ("站在黑雾里（留{e_zs}秒）时隐身。随后冲刺并吐出亡魂", "隐身{e_hide}秒。W 千载幽咽：冲刺并吐出亡魂")],
    "zh-hant": [("：黑霧升起，", "（擴充包）：敵方英雄靠近時黑霧自己升起（每{e_cd}秒最多一次），"),
                ("站在黑霧裡（留{e_zs}秒）時隱身。隨後衝刺並吐出亡魂", "隱身{e_hide}秒。W 冥魂之噬：衝刺並吐出亡魂")],
    "en": [(": mist rises - ", " (add-on): the mist rises by itself when an enemy champion comes near (once every {e_cd}s) - "),
           ("hidden while in the mist ({e_zs}s). Then he dashes", "hidden {e_hide}s. W Spectral Maw: he dashes")],
    "ko": [(": 안개가 일어 ", "(확장팩): 적 챔피언이 가까이 오면 안개가 저절로 일어 ({e_cd}초마다 최대 1번) "),
           ("안개 속({e_zs}초)에서는 은신. 이어서 돌진하며", "{e_hide}초 은신. W 망령의 나락: 돌진하며")],
    "ja": [("：霧が立ちのぼり", "（拡張）：敵チャンピオンが近づくと霧が自然に立ちのぼり（{e_cd}秒に1回まで）"),
           ("霧の中（{e_zs}秒）では透明。続けて突進し", "{e_hide}秒透明。W 亡霊の嘆き：突進し")],
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def souls(game):
    """champion id -> (category, sorted animation tags)."""
    import bundle_tool as B
    b = B.Bundle(B.find_game_dir(game))
    sheet = b.read_json("asset/base/setting/champion_info")
    out = {}
    base = [(k, v) for k, v in sheet.items() if isinstance(v, dict) and "attack" in v]
    base += [(c["id"], c) for c in sheet.get("mod_champions", [])]
    for cid, v in base:
        sprite = v.get("sprite") or f"asset/base/aseprite_resources/champions/{cid}"
        tags = b.anim_tags(sprite)
        if tags and v.get("category") in CATS:
            out[cid] = (CATS[v["category"]], sorted(tags))
    for pack in ("league", "tft"):
        for path in sorted(glob.glob(os.path.join(ROOT, pack, "champion", "*.data_champion"))):
            c = load(path)
            anim = os.path.join(ROOT, pack, "champions", os.path.basename(c["sprite"]) + "#anim.fanim")
            if not os.path.exists(lp(anim)) or c.get("category") not in CATS:
                continue
            out[c["id"]] = (CATS[c["category"]], sorted(load(anim).get("anims", {}).keys()))
    return dict(sorted(out.items()))


def souls_rs(table):
    lines = ["//! Every champion the add-on can draw Viego as: id -> (soul kit category, the animation tags of its sheet).",
             "//! Generated by make_override.py from the base game's champion sheet and this pack's heroes - do not edit by hand.",
             "", "pub const SOULS: &[(&str, &str, &[&str])] = &["]
    for cid, (cat, tags) in table.items():
        lines.append(f'    ("{cid}", "{cat}", &[{", ".join(json.dumps(t) for t in tags)}]),')
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
        sys.exit("the main pack's league_viego differs from build_viego.P: rebuild it first")
    q = dict(p, native=1)
    champion = kit.build(q)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":possess":
        sys.exit("the copy has no league_viego_soul:possess passive: update build_viego.py")
    for name in ("league_viego_mark", "league_viego_p_go", "league_viego_p_off", "league_viego_soul_melee",
                 "league_viego_p_on", "league_viego_shape"):
        if name not in json.dumps(champion):
            sys.exit(f"{name} is gone from the copy: update src/lib.rs")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.attack"
    champion["skill2"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.skill2"

    v = {k: p[k] for k in ("p_ad", "p_as")}
    v.update({k: setup.secs(p[k]) for k in ("p_win", "p_t", "p_inv", "soul_t")})
    texts = {lang: t.format(**v) for lang, t in TEXT.items()}
    long = {lang: setup.shown_length(t) for lang, t in TEXT.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    w_src = {}
    for lang, pairs in W_SWAP.items():
        src = setup.TEXT[lang]["skill2"]
        for old, new in pairs:
            if src.count(old) != 1:
                sys.exit(f"{lang}.skill2: {old!r} is not once in setup_viego.TEXT")
            src = src.replace(old, new)
        w_src[lang] = src
    wv = setup.values(p)
    wv.update({k: setup.secs(p[k]) for k in ("e_cd", "e_hide")})
    w_texts = {lang: t.format(**wv) for lang, t in w_src.items()}
    long = {lang: setup.shown_length(t) for lang, t in w_texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("W tooltip too long for the details panel: %s" % long)
    main_text = load(os.path.join(ROOT, "league", "text", "champion.i18n"))
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    copy_text = json.dumps(champion, ensure_ascii=False, indent=2) + "\n"
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    text_text = json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang], "skill2": w_texts[lang]}}}
                            for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n"
    if a.check:
        generated.check(MOD_ID, [(out, copy_text), (out_text, text_text)], ["src/souls.rs"])
        return
    table = souls(a.game)
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(copy_text)
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(text_text)
    with open(lp(os.path.join(ADDON, "src", "souls.rs")), "w", encoding="utf-8", newline="\n") as f:
        f.write(souls_rs(table))
    cats = {}
    for c, _ in table.values():
        cats[c] = cats.get(c, 0) + 1
    print("wrote", os.path.relpath(out, ROOT), os.path.relpath(out_text, ROOT), "src/souls.rs -", len(table),
          "champions", cats)
    print("tooltip lengths", {lang: f"{setup.shown_length(TEXT[lang])}/{setup.TOOLTIP_MAX[lang]}" for lang in TEXT})
    print("W tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in w_texts.items()})


if __name__ == "__main__":
    main()
