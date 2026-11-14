"""Build the add-on's copy of Yorick from the main pack (graves from kills, the Maiden's bonus on her target, the walkers
and the Maiden units of their own - as in League).

    python addons/league_yorick/make_override.py [--draft] [--check]

Rebuilds Yorick with tools/kit/build_yorick.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_yorick.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_yorick/override/league_yorick.data_champion and
.../text/champion.i18n: the build with native=1 -
  * passive = league_yorick:shepherd (params r_pct g_t);
  * Last Rites' blow raises `q_win` on him (the add-on digs a grave for each minion or monster that dies meanwhile) in
    place of the main pack's every-second-blow grave;
  * the ult puts `maiden` on her champion and his attacks a 3-tick `hit` on the champions they strike while she stands
    (the add-on deals the bonus on her target only), in place of the main pack's bonus on any champion;
  * 0.2.0, the summons as units (src/lib.rs; tools/art/unit_yorick_summons.py draws their sheets): the Awakening's cast
    takes `K_UNIT` off him and lays `K_ASK` (3 ticks) on its target, and the three walkers riding on the target play only
    without `K_UNIT` (the passive spawns them as units and lays the flag when the host gives units); Mourning Mist's
    champion twin lays `E_ASK` on the champion it strikes (the walker units leap to him); R takes `M_UNIT` off and lays
    `M_ASK` on its champion, and the riding Maiden with her two walkers (her rising, her claws, her picture) plays only
    without `M_UNIT`. The numbers the units use (WALK_*, LEAP_*, MAID_*, K_N, R_N ...) are checked against P and the
    unit sheets' attack frames: change the main pack and this script stops until lib.rs follows;
  * the attack's and the ult's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Yorick changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yorick")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_yorick as kit  # noqa: E402
import setup_yorick as setup  # noqa: E402

MOD_ID = "league_yorick"
HERO = "league_yorick"
KEYS = ("r_pct", "g_t")
UNITS = os.path.join(ROOT, "league", "champions")
phys, t, n, cc = setup.phys, setup.t, setup.n, setup.cc
# lang -> the add-on's attack and ult texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】抡铲。" + n("牧魂人") + "：临终仪式打英雄或打死单位挖一座坟，满{g_n}座时下一铲在目标身边唤醒{k_n}只" +
                  n("雾行者") + "，自己追咬敌人" + t("{walk_t}秒") + "（每口" + phys("k_dmg", "k_ratio") + "，可被击杀），同时" +
                  n("暗灵缠身") + "把附近的敌方英雄" + cc("定身") + t("{w_root}秒") + "。",
        "ult": "【附加包】在敌方英雄身后召唤" + n("迷雾室女") + "和{r_n}只雾行者，自己追击敌人" + t("{maid_t}秒") + "，她" + t("每秒") +
               "抓" + phys("r_dmg", "r_ratio") + "，可被击杀；她在场时约里克普攻她的目标额外造成最大生命{r_pct}%真实伤害。",
    },
    "zh-hant": {
        "attack": "【附加包】揮鏟。" + n("亡魂牧人") + "：臨終葬儀打英雄或打死單位挖一座墳，滿{g_n}座時下一鏟在目標身邊喚醒{k_n}隻" +
                  n("霧行者") + "，自己追咬敵人" + t("{walk_t}秒") + "（每口" + phys("k_dmg", "k_ratio") + "，可被擊殺），同時" +
                  n("黯影屍陣") + "把附近的敵方英雄" + cc("定身") + t("{w_root}秒") + "。",
        "ult": "【附加包】在敵方英雄身後召喚" + n("迷霧少女") + "和{r_n}隻霧行者，自己追擊敵人" + t("{maid_t}秒") + "，她" + t("每秒") +
               "抓" + phys("r_dmg", "r_ratio") + "，可被擊殺；她在場時約瑞科普攻她的目標額外造成最大生命{r_pct}%真實傷害。",
    },
    "en": {
        "attack": "[Add-on] Shovel blows. " + n("Shepherd of Souls") + ": Last Rites digs a grave on a champion or on a unit it "
                  "kills; with {g_n} graves the next one raises {k_n} " + n("Mist Walkers") + " beside the target that hunt on "
                  "their own for " + t("{walk_t}s") + " (" + phys("k_dmg", "k_ratio") + " a bite; they can be killed), and " +
                  n("Dark Procession") + " " + cc("roots") + " the enemy champions near it for " + t("{w_root}s") + ".",
        "ult": "[Add-on] Raises the " + n("Maiden of the Mist") + " and {r_n} walkers behind an enemy champion; they hunt on their "
               "own for " + t("{maid_t}s") + ", she claws for " + phys("r_dmg", "r_ratio") + " " + t("every second") + " and can "
               "be killed, and while she stands his attacks on her target deal {r_pct}% max health more as true damage.",
    },
    "ko": {
        "attack": "[확장] 삽 공격. " + n("영혼의 길잡이") + ": 최후의 의식으로 챔피언을 치거나 유닛을 처치하면 무덤 생성, {g_n}개가 차면 "
                  "다음 일격에 대상 곁에서 " + n("안개 망령") + " {k_n}마리가 일어나 " + t("{walk_t}초") + " 동안 스스로 적을 물어뜯음(한 번에 " +
                  phys("k_dmg", "k_ratio") + ", 처치 가능), " + n("망자의 진") + "이 주변 적 챔피언 " + t("{w_root}초") + " " + cc("속박") +
                  ".",
        "ult": "[확장] 적 챔피언 뒤에 " + n("안개 처녀") + "와 망령 {r_n}마리 소환, " + t("{maid_t}초") + " 동안 스스로 적을 쫓으며 " +
               t("매초") + " " + phys("r_dmg", "r_ratio") + "(처치 가능); 처녀가 있는 동안 요릭이 그 대상을 공격하면 최대 체력 {r_pct}% 고정 "
               "피해 추가.",
    },
    "ja": {
        "attack": "【拡張】シャベル攻撃。" + n("魂の導き手") + "：葬送でチャンピオンを打つかユニットを倒すと墓を掘る、{g_n}つ溜まると次の一撃で" +
                  "対象のそばに" + n("ミストウォーカー") + "{k_n}体が現れ" + t("{walk_t}秒") + "自ら噛みつく（1回" + phys("k_dmg", "k_ratio") +
                  "、倒せる）、" + n("屍の列") + "が周囲の敵チャンピオンを" + t("{w_root}秒") + cc("スネア") + "。",
        "ult": "【拡張】敵チャンピオンの背後に" + n("霧の乙女") + "とウォーカー{r_n}体を召喚、" + t("{maid_t}秒") + "自ら敵を追い" + t("毎秒") +
               phys("r_dmg", "r_ratio") + "、倒せる；乙女がいる間ヨリックがその対象を攻撃すると最大体力{r_pct}%の確定ダメージ。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def replace(o, match, make, count):
    """the tree with every dict `match` takes replaced by `make` of it (counted in `count`)"""
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


NONE = {"type": "Combine", "effects": []}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def mark(name):
    """3 ticks on the effect's target: the passive's ask"""
    return {"type": "AddBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": 3}}}}


def unless(flag, *effects):
    return {"type": "SwitchByBuff", "buff_name": flag, "effect_buff": NONE,
            "effect_none": {"type": "Combine", "effects": list(effects)}}


def attack_ticks(name):
    """a unit sheet's attack: (ticks long, the tick its third frame starts - the bite / the claws)"""
    with open(lp(os.path.join(UNITS, name + "#anim.fanim")), encoding="utf-8-sig") as f:
        frames = json.load(f)["anims"]["attack"]["frames"]
    secs = [fr.get("duration", fr["data"].get("duration")) for fr in frames]
    return round(sum(secs) * 60), round(sum(secs[:2]) * 60)


def units(champion, p, c):
    """0.2.0: the copy asks for the walkers and the Maiden as units; the riding ones play only without the flags. The
    natives' numbers (c: src/lib.rs) checked against P and the unit sheets."""
    want = {"K_N": p["k_n"], "WALK_HIT": p["k_dmg"], "WALK_HIT_AD": p["k_ratio"], "WALK_COOL": p["k_p"], "K_T": p["k_t"],
            "LEAP_HIT": p["k_jmp"], "LEAP_HIT_AD": p["k_jmp_r"], "R_N": p["r_n"], "MAID_HIT": p["r_dmg"],
            "MAID_HIT_AD": p["r_ratio"], "MAID_COOL": p["r_p"], "R_T": p["r_t"], "Q_HIT": p["q_hit"], "R_REL": p["r_rel"]}
    for name, act, lands in ((c["WALKER"], "WALK_ACT", "WALK_LANDS"), (c["MAIDEN_UNIT"], "MAID_ACT", "MAID_LANDS")):
        want[act], want[lands] = attack_ticks(name)
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the units' numbers differ from src/lib.rs (lib, kit or sheet): {wrong}")
    views = {v["name"] for v in champion["view_effects"]}
    kit = json.dumps(champion)
    if c["K_LEAP_VIEW"] not in views:
        sys.exit(f"src/lib.rs's K_LEAP_VIEW = {c['K_LEAP_VIEW']} is no view effect of the main pack's Yorick")
    for k in ("K_SPAWN_SFX", "K_LEAP_VIEW", "R_SPAWN_SFX"):
        if not re.search(r'"type": "(Target)?Sfx", "name": "' + re.escape(c[k]) + '"', kit):
            sys.exit(f"src/lib.rs's {k} = {c[k]} is no sound the main pack's Yorick plays")
    names = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    names |= {x.get("name") for x in walk(champion) if x.get("type") == "RemoveCasterBuff"}
    names |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if any(c[k] in names for k in ("K_ASK", "K_UNIT", "M_ASK", "M_UNIT", "E_ASK")) or \
            any(str(b).startswith((c["W_UID"], c["M_UID"])) for b in names):
        sys.exit("the main pack's Yorick already uses one of the add-on's buff names: update src/lib.rs")
    if c["R_ON"] not in names or c["MAIDEN"] not in names:
        sys.exit("the copy no longer has the flag r_on or the Maiden's mark: update src/lib.rs")

    def counted(found, n, what):
        if len(found) != n:
            sys.exit(f"{what}: {len(found)} found, not {n} (the slot's and the two controllers'): update this script")

    # the Awakening's cast (the animation it switches to with three graves): the flag off, the ask on its target
    found = []
    champion = replace(champion, lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == "league_yorick_g3"
                       and o["effect_buff"].get("type") == "CasterAnimation" and o["effect_buff"].get("name") == "awaken",
                       lambda o: dict(o, effect_buff={"type": "Combine", "effects": [o["effect_buff"], rm(c["K_UNIT"]),
                                                                                     mark(c["K_ASK"])]}), found)
    counted(found, 3, "the Awakening's cast")

    # the walkers riding on the Awakening's target: only without K_UNIT
    def raise_(o):
        effs = o["applied_effects"]
        kinds = [e["effect"].get("type") for e in effs]
        riding = json.dumps(effs[0]["effect"])
        if kinds != ["Combine", "ParabolicProjectile"] or "league_yorick_k_on" not in riding or \
                "league_yorick_k_bite" not in riding:
            sys.exit("the Awakening's walkers (league_yorick_q_raise) changed in the main pack: update this script")
        return dict(o, applied_effects=[dict(effs[0], effect=unless(c["K_UNIT"], effs[0]["effect"]))] + effs[1:])
    found = []
    champion = replace(champion, lambda o: o.get("type") == "TargetProjectile" and o.get("name") == "league_yorick_q_raise",
                       raise_, found)
    counted(found, 3, "league_yorick_q_raise")

    # the mist's champion twin: the pounce's ask on the champion it strikes, once a cast (inside its e_lk lock)
    def twin(o):
        effs = o["applied_effects"]
        sw = effs[0]["effect"] if len(effs) == 1 else {}
        once = sw.get("effect_none", {})
        if sw.get("type") != "SwitchByBuff" or sw.get("buff_name") != "league_yorick_e_lk" or once.get("type") != "Combine":
            sys.exit("Mourning Mist's champion twin (league_yorick_e_tw) changed in the main pack: update this script")
        return dict(o, applied_effects=[dict(effs[0], effect=dict(sw, effect_none=dict(
            once, effects=once["effects"] + [mark(c["E_ASK"])])))])
    found = []
    champion = replace(champion, lambda o: o.get("type") == "TargetProjectile" and o.get("name") == "league_yorick_e_tw",
                       twin, found)
    counted(found, 3, "league_yorick_e_tw")

    # R: the flag off and the ask on its champion at the cast; the riding Maiden and her walkers only without M_UNIT
    ult = champion["ult"]
    ult["effect"] = dict(ult["effect"], effects=ult["effect"]["effects"] + [rm(c["M_UNIT"]), mark(c["M_ASK"])])

    def rise(o):
        effs = o["applied_effects"]
        kinds = [e["effect"].get("type") for e in effs]
        if kinds != ["ViewEffect", "TargetSfx", "Combine", "AddCasted", "AddCasted", "SwitchByBuff", "AddBuff"] or \
                effs[0]["effect"].get("name") != "league_yorick_r_spawn" or \
                effs[6]["effect"]["buff_state"]["name"] != c["MAIDEN"]:
            sys.exit("the Maiden's rising (league_yorick_r_rise) changed in the main pack: update this script")
        riding = {"casting_type": effs[0]["casting_type"], "effect": unless(c["M_UNIT"], *[e["effect"] for e in effs[:5]])}
        return dict(o, applied_effects=[riding] + effs[5:])
    found = []
    champion["ult"] = replace(ult, lambda o: o.get("type") == "TargetProjectile" and o.get("name") == "league_yorick_r_rise",
                              rise, found)
    if len(found) != 1:
        sys.exit("R raises the Maiden %d times, not once: update this script" % len(found))
    return champion


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (r_pct: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":shepherd":
        sys.exit("the copy does not call the add-on: update this script")
    c = consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read())
    champion = units(champion, p, c)
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_yorick differs from build_yorick.P: rebuild it first")
        for slot in ("attack", "ult"):
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = dict(setup.values(p), walk_t=setup.secs(c["WALK_LIFE"]), maid_t=setup.secs(c["MAID_LIFE"]))
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
