"""Build the add-on's copy of Norra from the tft pack (Wild Rift's trinkets one by one, ability hits cutting their
cooldown, Memory Surge on the Threads and priming the trinkets, Journey to Nowhere any time, Portalpalooza!'s yarn balls).

    python addons/tft_norra/make_override.py [--draft] [--check]

Rebuilds Norra with tools/kit/build_norra.py (its parameter table P), checks that the plain build is the tft pack's
tft/champion/tft_norra.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/tft_norra/override/tft_norra.data_champion and
.../text/champion.i18n: the build with --native (build_norra.py) -
  * passive = tft_norra:trinkets (params build_norra.NATIVE_KEYS): Journey to Nowhere on whoever comes close;
  * a ready Q / E landing calls tft_norra:drop (the add-on's trinkets instead of the field), Memory Surge's hits
    tft_norra:surge (the max-health bonus, the Threads, the trinkets primed, their cooldown cut) instead of the Threads
    zone and the primed field, Threads of Homecoming's hits tft_norra:refund, the rift tft_norra:rift (the yarn balls
    instead of the four volleys over everyone inside); the attack opens no portal;
  * the views the add-on plays: the trinkets' three pieces, the flying yarn ball (tools/art/import_norra_fx.py);
  * every slot's tooltip says the add-on's rules, tagged (the add-on's id is the hero's: its texts merge over the tft
    pack's), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the tft pack's Norra changes.
--draft: only the copy, without the tft-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "tft_norra")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_norra as kit  # noqa: E402
import setup_norra as setup  # noqa: E402

MOD_ID = "tft_norra"
HERO = "tft_norra"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")
mag, t, n, cc, AD, M, E = setup.mag, setup.t, setup.n, setup.cc, setup.AD, setup.M, setup.E
TAG = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
# lang -> the add-on's texts (Threads of Homecoming's is the tft pack's: its new rule, the cooldown cut, is the passive's)
NATIVE = {
    "zh-hans": {
        "attack": "普攻" + AD + n("物理伤害") + "。" + n("寄情琐物") + "：每" + t("{p_cd}秒") + "技能落点撒3个琐物" + t("{p_life}秒") +
                  "，飞向踩到的敌方英雄：" + mag("p_dmg", "p_ratio") + "魔法伤害并挂" + n("线缕") + "；技能命中英雄冷却-20%。" + n("奇异旅程") +
                  "：贴身的敌人受" + mag("w_dmg", "w_ratio") + "魔法伤害，" + cc("放逐") + t("{w_t}秒") + "后" + cc("减速") + "{w_slow}%" +
                  t("{w_slow_t}秒") + "。",
        "skill": "蓄力后射出回忆魔法弹，自己后退一步：落点周围敌人受到" + mag("q_dmg", "q_ratio") + "魔法伤害，已有" + n("线缕") +
                 "的英雄再受最大生命{q_bonus}%，随后挂上线缕；打中英雄时地上的琐物待爆：敌方英雄靠近就飞向他。",
        "ult": "在敌方英雄脚下展开大裂隙，每" + t("{r_gap}秒") + "一波共4波：两个毛线球沿一条穿过敌方英雄的线从两头对飞，路上敌人各受" +
               mag("r_dmg", "r_ratio") + "魔法伤害，每个球碰到的第一个英雄" + cc("减速") + "{r_slow}%" + t("{r_slow_t}秒") + "；第4波+{r_last}%。",
    },
    "zh-hant": {
        "attack": "普攻" + AD + n("物理傷害") + "。" + n("心愛飾品") + "：每" + t("{p_cd}秒") + "技能落點撒3個飾品" + t("{p_life}秒") +
                  "，飛向踩到的敵方英雄：" + mag("p_dmg", "p_ratio") + "魔法傷害並掛" + n("絲線") + "；技能命中英雄冷卻-20%。" + n("茫然旅程") +
                  "：貼身的敵人受" + mag("w_dmg", "w_ratio") + "魔法傷害，" + cc("放逐") + t("{w_t}秒") + "後" + cc("緩速") + "{w_slow}%" +
                  t("{w_slow_t}秒") + "。",
        "skill": "蓄力後射出記憶魔法彈，自己後退一步：落點周圍敵人受到" + mag("q_dmg", "q_ratio") + "魔法傷害，已有" + n("絲線") +
                 "的英雄再受最大生命{q_bonus}%，隨後掛上絲線；打中英雄時地上的飾品待爆：敵方英雄靠近就飛向他。",
        "ult": "在敵方英雄腳下展開大裂隙，每" + t("{r_gap}秒") + "一波共4波：兩個毛線球沿一條穿過敵方英雄的線從兩頭對飛，路上敵人各受" +
               mag("r_dmg", "r_ratio") + "魔法傷害，每個球碰到的第一個英雄" + cc("緩速") + "{r_slow}%" + t("{r_slow_t}秒") + "；第4波+{r_last}%。",
    },
    "en": {
        "attack": "Star bolt: " + AD + " " + n("physical damage") + ". " + n("Beloved Trinkets") + ": every " + t("{p_cd}s") +
                  " the next ability drops 3 trinkets (" + t("{p_life}s") + "), each flying to the champion stepping on it: " +
                  mag("p_dmg", "p_ratio") + " " + M + "magic damage" + E + " + " + n("Threads") + "; ability hits on champions cut "
                  "it 20%. " + n("Journey to Nowhere") + ": a close enemy champion takes " + mag("w_dmg", "w_ratio") + ", is " +
                  cc("banished") + " " + t("{w_t}s") + ", then " + cc("slowed") + " {w_slow}% " + t("{w_slow_t}s") + ".",
        "skill": "Charges, then flings a bolt of memories and hops back: enemies around where it lands take " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ", champions already in the " + n("Threads") + " {q_bonus}% "
                 "of their max health more, then get them. Hitting a champion primes her trinkets: they fly to any enemy "
                 "champion coming near.",
        "ult": "Opens a great rift under an enemy champion: 4 recasts " + t("{r_gap}s") + " apart, each sending a yarn ball from "
               "both ends along a line through an enemy champion: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               " to every enemy on it, the first champion each ball meets " + cc("slowed") + " {r_slow}% for " +
               t("{r_slow_t}s") + "; the 4th deals {r_last}% more.",
    },
    "ko": {
        "attack": "별빛 탄환 " + AD + " 물리 피해. " + n("소중한 장신구") + ": " + t("{p_cd}초") + "마다 스킬 착지점에 장신구 3개(" +
                  t("{p_life}초") + "), 밟은 적에게 날아가 " + mag("p_dmg", "p_ratio") + " 마법 피해와 " + n("실타래") + ". 스킬이 챔피언 "
                  "적중 시 대기시간 -20%. " + n("미지로의 여정") + ": 붙은 적 챔피언에게 " + mag("w_dmg", "w_ratio") + " 마법 피해, " +
                  t("{w_t}초") + " " + cc("추방") + " 뒤 " + t("{w_slow_t}초") + " {w_slow}% " + cc("둔화") + ".",
        "skill": "충전 후 기억의 탄환을 날리고 뒤로 물러난다: 떨어진 곳 주변 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해, " +
                 n("실타래") + "가 있던 챔피언은 최대 체력 {q_bonus}% 추가 후 실타래. 챔피언에게 맞으면 장신구가 가까이 온 적 챔피언에게 날아간다.",
        "ult": "적 챔피언 발밑에 큰 균열을 열고 " + t("{r_gap}초") + "마다 4번: 양 끝에서 털실 뭉치가 적 챔피언을 지나는 선을 따라 날아가 선 위의 "
               "적에게 " + mag("r_dmg", "r_ratio") + " 마법 피해, 각 뭉치에 처음 맞은 챔피언은 " + t("{r_slow_t}초") + " {r_slow}% " +
               cc("둔화") + ", 4번째는 +{r_last}%.",
    },
    "ja": {
        "attack": "星の弾で" + AD + "物理ダメージ。" + n("愛用のトリンケット") + "：" + t("{p_cd}秒") + "毎、スキル着弾点に3つ" +
                  t("{p_life}秒") + "、踏んだ敵チャンピオンへ飛び" + mag("p_dmg", "p_ratio") + "魔法ダメージと" + n("スレッド") +
                  "。スキル命中でCD-20%。" + n("どこでもない場所へ") + "：密着した敵に" + mag("w_dmg", "w_ratio") + "、" + t("{w_t}秒") +
                  cc("追放") + "後" + t("{w_slow_t}秒") + "{w_slow}%" + cc("スロウ") + "。",
        "skill": "溜めてから記憶の弾を放ち、後ろへ跳ぶ：着弾点の周りの敵に" + mag("q_dmg", "q_ratio") + "魔法ダメージ、" + n("スレッド") +
                 "付きのチャンピオンには最大体力{q_bonus}%追加、その後スレッド。チャンピオンに当たるとトリンケットが近づく敵へ飛ぶ。",
        "ult": "敵チャンピオンの足元に大きな裂け目を開き、" + t("{r_gap}秒") + "毎に4回、両端から毛糸玉が敵チャンピオンを通る線を飛ぶ：線上の敵に" +
               mag("r_dmg", "r_ratio") + "魔法ダメージ、各玉が最初に当たったチャンピオンに" + t("{r_slow_t}秒") + "{r_slow}%" + cc("スロウ") +
               "、4回目は+{r_last}%。",
    },
}
for _lang, _d in NATIVE.items():
    _d["skill2"] = setup.TEXT[_lang]["skill2"]
    for _k in SLOTS:
        _d[_k] = TAG[_lang] + _d[_k]


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(KEYS):
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}, keys {sorted(set(got) ^ set(KEYS))}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(p, True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":trinkets":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "tft", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the tft pack's tft_norra differs from build_norra.P: rebuild it first")
        values = setup.values(p)
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "tft", "text", "champion.i18n")), encoding="utf-8-sig") as f:
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
