"""Build the add-on's copy of Ambessa from the main pack (the sweep's edge, the slam's first, the brace when struck, the
farthest execution, as in League).

    python addons/league_ambessa/make_override.py [--draft] [--check]

Rebuilds Ambessa with tools/kit/build_ambessa.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_ambessa.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_ambessa/override/league_ambessa.data_champion
and .../text/champion.i18n: the build with native=1 -
  * passive = league_ambessa:matriarch (params: build_ambessa.ADDON_KEYS);
  * Cunning Sweep marks what it hits (`q_edge`) without the % max-health part, the add-on deals it at the blade's edge;
  * Sundering Slam marks what the line hits (`q2_first`), the add-on gives the bonus to the first enemy on it;
  * Repudiation's slam deals its % max-health part only with `w_hit`, raised by the add-on when she is struck braced;
  * Public Execution only marks its champion (`r_aim`, `r_go`): the add-on blinks, pins, slams and fires the combos;
  * the attack's (passive + Repudiation), Q's and R's tooltips (keys of the add-on's own id) say the League rules, so the
    tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Ambessa changes.
--draft: only the copy, without the main-pack check and the texts (for a kit not yet in the main pack; the texts take
tools/kit/setup_ambessa.py's values(p): the keys NATIVE uses, the durations in seconds). --check:
write nothing, exit 1 when the files on disk are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ambessa")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_ambessa as kit  # noqa: E402

MOD_ID = "league_ambessa"
HERO = "league_ambessa"
KEYS = kit.ADDON_KEYS
O, A, R, E = "<#ff9028ff>", "<#ffb900ff>", "<#ef5350ff>", "<>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


# lang -> the add-on's attack (passive + Repudiation), Q and R texts (the main pack's with the add-on's rules; League's
# names, Data Dragon 16.21.1, as tools/kit/setup_ambessa.py); no combo sentence (the combos are the README's)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】双刀。" + n("龙犬诡步") + "：每放一个技能就朝目标冲一步，下一刀更快更重。" + n("铁令") +
                  "：敌方英雄靠近时举刀格挡得到护盾，然后砸地" + phys("w_dmg", "w_ratio") + "；格挡时挨了英雄或野怪的打，砸地再加最大生命{w_pct}%。",
        "skill": "【附加包】" + n("暗袭") + "向前扫半圈" + phys("q_dmg", "q_ratio") + "，刀尖扫到的再加最大生命{q_pct}%；扫中后可接" +
                 n("裂斩") + "：直线劈下" + phys("q2_dmg", "q2_ratio") + "，第一个敌人再加最大生命{q2_pct}%。",
        "ult": "【附加包】闪到她和目标这条线上最远的敌方英雄身边，" + cc("压制") + t("{r_sup}秒") + "后砸进地里：" +
               phys("r_dmg", "r_ratio") + " + 最大生命{r_pct}%，" + cc("眩晕") + t("{r_stun}秒") + "。",
    },
    "zh-hant": {
        "attack": "【附加包】雙刀。" + n("龍犬詭步") + "：每放一個技能就朝目標衝一步，下一刀更快更重。" + n("鐵令") +
                  "：敵方英雄靠近時舉刀格擋得到護盾，然後砸地" + phys("w_dmg", "w_ratio") + "；格擋時挨了英雄或野怪的打，砸地再加最大生命{w_pct}%。",
        "skill": "【附加包】" + n("暗襲") + "向前掃半圈" + phys("q_dmg", "q_ratio") + "，刀尖掃到的再加最大生命{q_pct}%；掃中後可接" +
                 n("裂斬") + "：直線劈下" + phys("q2_dmg", "q2_ratio") + "，第一個敵人再加最大生命{q2_pct}%。",
        "ult": "【附加包】閃到她和目標這條線上最遠的敵方英雄身邊，" + cc("壓制") + t("{r_sup}秒") + "後砸進地裡：" +
               phys("r_dmg", "r_ratio") + " + 最大生命{r_pct}%，" + cc("暈眩") + t("{r_stun}秒") + "。",
    },
    "en": {
        "attack": "[Add-on] Twin blades. " + n("Drakehound's Step") + ": every ability ends in a dash at her target and a "
                  "faster, harder next attack. " + n("Repudiation") + ": with an enemy champion close she braces behind her "
                  "raised blade for a shield, then slams for " + phys("w_dmg", "w_ratio") + "; struck by a champion or "
                  "monster while braced, the slam adds {w_pct}% max health.",
        "skill": "[Add-on] " + n("Cunning Sweep") + " in a half circle for " + phys("q_dmg", "q_ratio") + ", {q_pct}% max "
                 "health more at the blade's edge; on a hit " + n("Sundering Slam") + " follows down a line for " +
                 phys("q2_dmg", "q2_ratio") + ", the first enemy taking {q2_pct}% max health more.",
        "ult": "[Add-on] Blinks to the farthest enemy champion on the line through her target and " + cc("suppresses") +
               " it for " + t("{r_sup}s") + ", then slams it down for " + phys("r_dmg", "r_ratio") + " + {r_pct}% max health, " +
               cc("stunning") + " for " + t("{r_stun}s") + ".",
    },
    "ko": {
        "attack": "[확장] 쌍검. " + n("용사냥개의 발걸음") + ": 스킬마다 대상에게 짧게 돌진하고 다음 공격이 더 빠르고 강해짐. " + n("배척") +
                  ": 적 챔피언이 가까우면 검을 들어 막아 보호막을 얻고 내려찍어 " + phys("w_dmg", "w_ratio") +
                  "; 막는 동안 챔피언이나 몬스터에게 맞으면 최대 체력 {w_pct}% 추가.",
        "skill": "[확장] " + n("교활한 휩쓸기") + ": 반원으로 " + phys("q_dmg", "q_ratio") + ", 칼끝에 닿으면 최대 체력 {q_pct}% 추가; "
                 "적중 시 " + n("파멸의 일격") + ": 직선으로 " + phys("q2_dmg", "q2_ratio") + ", 첫 번째 적은 최대 체력 {q2_pct}% 추가.",
        "ult": "[확장] 대상 방향 직선 위 가장 먼 적 챔피언 옆으로 순간이동해 " + t("{r_sup}초") + " " + cc("제압") + " 후 내려찍어 " +
               phys("r_dmg", "r_ratio") + " + 최대 체력 {r_pct}%, " + t("{r_stun}초") + " " + cc("기절") + ".",
    },
    "ja": {
        "attack": "【拡張】双剣。" + n("ドレイクハウンドの猛攻") + "：スキルごとに対象へ短く突進し、次の攻撃が速く重くなる。" + n("断交") +
                  "：敵チャンピオンが近いと剣を掲げて防御しシールドを得てから叩きつけ" + phys("w_dmg", "w_ratio") +
                  "；構え中にチャンピオンかモンスターに殴られると最大体力{w_pct}%追加。",
        "skill": "【拡張】" + n("カニングスイープ") + "：半円に" + phys("q_dmg", "q_ratio") + "、刃先は最大体力{q_pct}%追加；命中すると" +
                 n("サンダリングスラム") + "：直線に" + phys("q2_dmg", "q2_ratio") + "、最初の敵は最大体力{q2_pct}%追加。",
        "ult": "【拡張】対象への直線上で最も遠い敵チャンピオンの側へ瞬間移動し" + t("{r_sup}秒") + cc("制圧") + "、叩きつけて" +
               phys("r_dmg", "r_ratio") + " + 最大体力{r_pct}%、" + t("{r_stun}秒") + cc("スタン") + "。",
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
    m = re.search(r"Self \{ (ctl_p: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(KEYS):
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad or sorted(set(got) ^ set(KEYS))}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":matriarch":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        import setup_ambessa as setup  # noqa: E402  her texts (the integration)
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_ambessa differs from build_ambessa.P: rebuild it first")
        for slot in ("attack", "skill", "ult"):
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
