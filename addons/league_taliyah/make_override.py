"""Build the add-on's copy of Taliyah from the main pack (Weaver's Wall as real terrain).

    python addons/league_taliyah/make_override.py [--check]

Rebuilds Taliyah with tools/kit/build_taliyah.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_taliyah.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs are P's numbers, and writes addons/league_taliyah/override/league_taliyah.data_champion and
.../text/champion.i18n: the build with native=1 -
  * passive league_taliyah:wall (params: r_t, r_w, r_h, r_seg, r_n, r_lay_speed);
  * the walls without the main pack's slow and drag (the add-on keeps every unit out), the `wall_up` / `lay_up` flags and
    the `aim` mark on R's target (the add-on finds the walls from them);
  * the ult's tooltip points to description.league_taliyah_addon.ult with the add-on's wording, so the tooltip in game
    shows whether the override took;
  * no surf from the data (0.2.8): the passive gives Rock Surfing near terrain (src/surf.rs, League's four steps by
    level, LEVEL_MS there), and the attack's tooltip (it carries the passive) points to
    description.league_taliyah_addon.attack, which says so.
Every other champion stays untouched. Run it again whenever the main pack's Taliyah changes; --check only compares.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_taliyah")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_taliyah as kit  # noqa: E402
import setup_taliyah as setup  # noqa: E402

TEXT_ID = "league_taliyah_addon"        # the texts' key (the hero's own id is league_taliyah)
HERO = "league_taliyah"
PARAMS = ("r_t", "r_w", "r_h", "r_seg", "r_n", "r_lay_speed")
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
t, cc, nm = setup.t, setup.cc, setup.n
TEXT = {
    "zh-hans": {
        "attack": "甩出一块石子。" + nm("浮石冲") + "：脱战时贴着地形或她的墙，移速渐强到+{lo}%～{hi}%（随等级）；放出墙幔后踩石冲浪，移速"
                  "+{r_ms}%（" + t("{r_surf}秒") + "）。",
        "ult": "敌人在附近或已在交战：在目标处竖起长石墙（" + t("{r_t}秒") + "），墙上的单位被推到她这一侧；敌人较远：从脚下拉出"
               "一道横墙，踩着石头沿墙冲刺，靠近敌人时跳下。墙是真的地形：英雄、小兵和野怪都过不去。",
    },
    "zh-hant": {
        "attack": "甩出一塊石子。" + nm("馭石之術") + "：脫戰時貼著地形或她的牆，移速漸強到+{lo}%～{hi}%（隨等級）；放出編織者之牆後踩石"
                  "衝浪，移速+{r_ms}%（" + t("{r_surf}秒") + "）。",
        "ult": "敵人在附近或已在交戰：在目標處豎起長石牆（" + t("{r_t}秒") + "），牆上的單位被推到她這一側；敵人較遠：從腳下拉出"
               "一道橫牆，踩著石頭沿牆衝刺，靠近敵人時跳下。牆是真的地形：英雄、小兵和野怪都過不去。",
    },
    "en": {
        "attack": "Flicks a pebble. " + nm("Rock Surfing") + ": out of a fight, near terrain or her walls, her move speed builds "
                  "to +{lo}-{hi}% (by level); after Weaver's Wall she surfs a boulder, +{r_ms}% move speed for " + t("{r_surf}s") + ".",
        "ult": "With an enemy champion near or a fight on: a long stone wall rises where the target stands for " +
               t("{r_t}s") + ", pushing units on it to her side. With the enemies far: a wall runs out from her feet and "
               "she surfs along its top, jumping off once enemies are near. The walls are real terrain: no champion, "
               "minion or monster can cross them.",
    },
    "ko": {
        "attack": "돌멩이를 던진다. " + nm("바위타기") + ": 전투 중이 아닐 때 지형이나 자신의 벽 근처에서 이동 속도가 +{lo}~{hi}%(레벨 비례)까지 "
              "점점 증가; 바위술사의 벽 후 바위를 타고 " + t("{r_surf}초") + " 동안 이동 속도 +{r_ms}%.",
        "ult": "적 챔피언이 가깝거나 교전 중: 대상 위치에 " + t("{r_t}초") + " 동안 긴 돌벽을 세우고 벽 위의 유닛을 자신 쪽으로 밀어냄. "
               "적이 멀면: 발밑에서 벽을 뻗어 바위를 타고 벽 위를 달리다 적이 가까워지면 뛰어내림. 벽은 진짜 지형: 챔피언도 "
               "미니언도 몬스터도 넘을 수 없음.",
    },
    "ja": {
        "attack": "小石を投げる。" + nm("ロックサーフィン") + "：戦闘外で地形や自分の壁の近くにいると移動速度が+{lo}～{hi}%（レベル比例）まで"
              "上昇；ウィーバーウォールの後は岩に乗り" + t("{r_surf}秒") + "移動速度+{r_ms}%。",
        "ult": "敵チャンピオンが近いか交戦中：対象の位置に" + t("{r_t}秒") + "長い石壁を立て、壁の上のユニットを自分の側へ押し出す。"
               "敵が遠い：足元から壁を伸ばし岩に乗って壁の上を進み、敵が近づくと飛び降りる。壁は本物の地形：チャンピオンも"
               "ミニオンもモンスターも越えられない。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """The numbers in src/lib.rs's `Params { r_t: 300, ... }` (Default)."""
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"Params \{ (r_t: \d+[^}]*)\}", src)
    if not m:
        sys.exit("no Params { r_t: ... } default in src/lib.rs: update this script")
    return {k: int(v) for k, v in re.findall(r"(\w+): (\d+)", m.group(1))}


def rock_steps():
    """src/surf.rs's LEVEL_MS: Rock Surfing's move speed by level (League's four steps)."""
    with open(lp(os.path.join(ADDON, "src", "surf.rs")), encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"pub const LEVEL_MS: \[i32; 4\] = \[([^\]]*)\];", src)
    if not m:
        sys.exit("no LEVEL_MS in src/surf.rs: update this script")
    return [int(x) for x in m.group(1).split(",")]


def main():
    check = "--check" in sys.argv[1:]
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_taliyah differs from build_taliyah.P: rebuild it first")
    want = {k: p[k] for k in PARAMS}
    if rust_defaults() != want:
        sys.exit(f"src/lib.rs's default Params {rust_defaults()} are not P's {want}: update them")
    champion = kit.build(dict(p, native=1))
    dump = json.dumps(champion)
    # the walls' slow (an AddBuff of r_stuck) gone, the marks the add-on reads there
    if (champion.get("passive", {}).get("passive_ref") != "league_taliyah:wall"
            or '"league_taliyah_r_stuck", "duration"' in dump
            or not all(f'"league_taliyah_{x}"' in dump for x in ("wall_up", "lay_up", "aim"))):
        sys.exit("the copy does not call the add-on: update this script")
    if '"name": "league_taliyah_surf", "duration": "Permanent", "move_speed_mult"' in dump:
        sys.exit("the copy still puts the data's surf on her (the add-on gives it near terrain): update build_taliyah.py")
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    steps = rock_steps()
    values = dict(setup.values(p), lo=steps[0], hi=steps[-1])
    texts = {lang: {k: (LEAD[lang] + v).format(**values) for k, v in tx.items()} for lang, tx in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + v) for lang, tx in TEXT.items() for k, v in tx.items()
            if setup.shown_length(LEAD[lang] + v) > setup.TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    files = {out: dumps_main(champion), tpath: dumps_main(i18n)}
    if check:
        stale = []
        for path, text in files.items():
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    if f.read() == text:
                        continue
            except FileNotFoundError:
                pass
            stale.append(os.path.relpath(path, ROOT))
        if stale:
            sys.exit("league_taliyah: stale %s - run python addons/league_taliyah/make_override.py" % ", ".join(stale))
        print("league_taliyah: %s up to date" % ", ".join(os.path.relpath(x, ROOT).replace(os.sep, "/") for x in files))
        return
    for path, text in files.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    for lang, tx in TEXT.items():
        print(lang, " ".join(f"{k}:{setup.shown_length(LEAD[lang] + v)}/{setup.TOOLTIP_MAX[lang]}" for k, v in tx.items()))
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
