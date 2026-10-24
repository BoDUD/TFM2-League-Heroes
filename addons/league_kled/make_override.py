"""Build the add-on's copy of Kled from the main pack (Skaarl's own health, the rope that snaps, as in League).

    python addons/league_kled/make_override.py [--draft] [--check]

Rebuilds Kled with tools/kit/build_kled.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_kled.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_kled/override/league_kled.data_champion and
.../text/champion.i18n: the build with native=1 -
  * passive = league_kled:skaarl (params sk_hp sk_ad re_hp re_ad q_break);
  * the mount and the remount raise a plain `sk` flag (the add-on counts Skaarl's health and takes it off), not the main
    pack's WithShield stand-in;
  * the attack's and the skill's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game
    shows whether the override took.
The whole body on foot is the add-on's view code (src/view.rs), nothing in the copy. Every other champion stays
untouched. Run it again whenever the main pack's Kled changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kled")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_kled as kit  # noqa: E402
import setup_kled as setup  # noqa: E402

MOD_ID = "league_kled"
HERO = "league_kled"
KEYS = ("sk_hp", "sk_ad", "re_hp", "re_ad", "q_break")
phys, sh, t, n, cc = setup.phys, setup.sh, setup.t, setup.n, setup.cc
# lang -> the add-on's attack and skill texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】挥斧。" + n("斯嘎尔") + "有自己的血（" + sh("sk_hp", "sk_ad") + "），替他挡伤害，打空就下马：攻击-{dm_atk}%，"
                  "不能比武、冲锋；打人攒勇气，满了上马。" + n("暴烈秉性") + "：每" + t("{w_cd}秒") + "四下快攻，第四下多" +
                  phys("w_dmg", "w_ratio") + "+最大生命{w_pct}%。",
        "skill": "【附加包】扔捕熊夹造成" + phys("q_dmg", "q_ratio") + "；夹住英雄" + cc("减速") + "{q_slow}%，" + t("{q_teth}秒") +
                 "后再造成" + phys("q2_dmg", "q2_ratio") + "并" + cc("拽过来") + "，它跑太远绳子会断。下马时是" + n("随身手枪") +
                 "：" + phys("p_dmg", "p_ratio") + "，自己往后跳。",
    },
    "zh-hant": {
        "attack": "【附加包】揮斧。" + n("小嘎") + "有自己的血（" + sh("sk_hp", "sk_ad") + "），替他擋傷害，打空就下馬：攻擊-{dm_atk}%，"
                  "不能比武、衝鋒；打人攢勇氣，滿了上馬。" + n("生性暴戾") + "：每" + t("{w_cd}秒") + "四下快攻，第四下多" +
                  phys("w_dmg", "w_ratio") + "+最大生命{w_pct}%。",
        "skill": "【附加包】丟出捕獸夾造成" + phys("q_dmg", "q_ratio") + "；夾住英雄" + cc("緩速") + "{q_slow}%，" + t("{q_teth}秒") +
                 "後再造成" + phys("q2_dmg", "q2_ratio") + "並" + cc("拉過來") + "，牠跑太遠繩子會斷。下馬時是" + n("隨身手槍") +
                 "：" + phys("p_dmg", "p_ratio") + "，自己往後跳。",
    },
    "en": {
        "attack": "[Add-on] Axe blows. " + n("Skaarl") + " has his own health (" + sh("sk_hp", "sk_ad") + ") and takes Kled's "
                  "damage; when it is gone Kled fights on foot: -{dm_atk}% attack, no Jousting, no charge; hitting enemies "
                  "builds courage to remount. " + n("Violent Tendencies") + ": every " + t("{w_cd}s") + " four fast attacks, "
                  "the fourth dealing " + phys("w_dmg", "w_ratio") + " + {w_pct}% max health more.",
        "skill": "[Add-on] Throws a bear trap for " + phys("q_dmg", "q_ratio") + "; a champion caught is " + cc("slowed") +
                 " {q_slow}%, then after " + t("{q_teth}s") + " takes " + phys("q2_dmg", "q2_ratio") + " and is " +
                 cc("yanked") + " - unless it ran far enough to snap the rope. On foot it is " + n("Pocket Pistol") + ": " +
                 phys("p_dmg", "p_ratio") + ", knocking him back.",
    },
    "ko": {
        "attack": "[확장] 도끼 공격. " + n("스칼") + "은 자기 체력(" + sh("sk_hp", "sk_ad") + ")으로 피해를 대신 받고, 바닥나면 걸어서 "
                  "싸움: 공격력 -{dm_atk}%, 이랴!·돌격 불가; 적을 치면 용기가 쌓여 다시 탑승. " + n("버럭버럭") + ": " +
                  t("{w_cd}초") + "마다 빠른 4회 공격, 4번째 " + phys("w_dmg", "w_ratio") + " + 최대 체력 {w_pct}%.",
        "skill": "[확장] 덫을 던져 " + phys("q_dmg", "q_ratio") + "; 걸린 챔피언 {q_slow}% " + cc("둔화") + ", " + t("{q_teth}초") +
                 " 뒤 " + phys("q2_dmg", "q2_ratio") + " 후 " + cc("끌어옴") + "(너무 멀어지면 줄이 끊김). 걸어서는 " +
                 n("주머니 권총") + ": " + phys("p_dmg", "p_ratio") + ", 뒤로 밀려남.",
    },
    "ja": {
        "attack": "【拡張】斧で攻撃。" + n("スカール") + "は自分の体力（" + sh("sk_hp", "sk_ad") + "）でダメージを肩代わり、尽きると徒歩："
                  "攻撃-{dm_atk}%、ジャウスト・突撃不可；敵を打つと勇気が溜まり再騎乗。" + n("狂暴の宴") + "：" + t("{w_cd}秒") +
                  "毎に4回の速攻、4回目" + phys("w_dmg", "w_ratio") + "+最大体力{w_pct}%。",
        "skill": "【拡張】トラバサミを投げ" + phys("q_dmg", "q_ratio") + "；捕えたチャンピオンを{q_slow}%" + cc("スロウ") + "、" +
                 t("{q_teth}秒") + "後に" + phys("q2_dmg", "q2_ratio") + "で" + cc("引き寄せ") + "（離れすぎるとロープが切れる）。"
                 "徒歩時は" + n("ポケットピストル") + "：" + phys("p_dmg", "p_ratio") + "、自分は後ろへ跳ぶ。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (sk_hp: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":skaarl":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_kled differs from build_kled.P: rebuild it first")
        for slot in ("attack", "skill"):
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = setup.values(p)
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
        print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
               for k, tx in d.items()})
    out[os.path.join(ADDON, "override", HERO + ".data_champion")] = dumps_main(champion)
    return out, champion


def main():
    draft = "--draft" in sys.argv[1:]
    out, champion = files(draft)
    if "--check" in sys.argv[1:]:
        stale = [os.path.relpath(path, ROOT) for path, text in out.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in out.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))
    print("(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
