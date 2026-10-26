"""Norra's text (5 languages), sound_info files and her keys in the tft pack's shared files, numbers from build_norra.P.

    python tools/kit/setup_norra.py [--params final.json] [--check]

Writes (in tft/, mod_id tft): text/champion.i18n (tft_norra in every language, description + skill_name),
sound/sfx/tft_norra_*.sound_info, mod.override_info (the text and champion_view merges, both entries of every sound:
its event -> our .sound_info, its clip -> our audio, the custom-sound rule), style/champion_view (face, centre) and
mod.mod_info (VERSION, the pack's description: setup_powder.DESC with every hero of HEROES). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against TOOLTIP_MAX.
Names: Wild Rift's own (her kit is Wild Rift's: the user, 2026-10-26, 「你要参照手游的技能啊」), from its champion pages
(ko-kr, ja-jp, zh-tw, en-us, 2026-10-26) and the Chinese release (zh-hans): 诺拉 / 諾拉 / Norra / 노라 / ノラ; Beloved
Trinkets 寄情琐物, Journey to Nowhere 奇异旅程 (both in the attack's text: TFM2 has three active slots), Memory Surge
回忆涌现, Threads of Homecoming 思乡线缕, Portalpalooza! 传送门欢腾！.
Sounds: League clips borrowed by tools/lol/extract_norra.py into tft/sound/sfx/tft_norra_sfx_*.wav (git-ignored) - the
user's call for her (2026-10-26: 「诺拉用抓好的英雄联盟音效」), unlike Powder's base-game mixes. A clip name never equals
an event name (vo-clip-names rule): event tft_norra_<x> plays clip tft_norra_sfx_<x>. package_mod moves the clips to
sound/bgm/ at install.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_norra import P, lp, MOD_ID, ID  # noqa: E402
import setup_powder as pack  # noqa: E402  the tft pack's name and description

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.2.0"
CLIP = f"{ID}_sfx_"
ADi, APi = pack.ADi, pack.APi
TOOLTIP_MAX = pack.TOOLTIP_MAX
M, O, A, R, E = pack.M, pack.O, pack.A, pack.R, pack.E
# champion_view: the face point between her eyes, under the tall hat (tfm2_ase.py face finds the hat's top 33 px up:
# a portrait round it showed the hat and no face - lint's warning stands, as for the base game's two big hats); her
# idle's top is 22 px over the pivot: the ban/pick card fits it, no banpick_center
VIEW = {"face": {"x": 1, "y": -20}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return pack.mag(d, r)


def t(s):
    return A + s + E


def n(s):
    return O + s + E


def cc(s):
    return R + s + E


AD = ADi + O + "100%" + E

TEXT = {
    "zh-hans": {
        "name": "诺拉",
        "attack": "星光弹造成" + AD + n("物理伤害") + "。" + n("寄情琐物") + "：每" + t("{p_cd}秒") + "，下个技能落点留下琐物" + t("{p_life}秒") +
                  "，走进的敌方英雄受到" + mag("p_dmg", "p_ratio") + "魔法伤害并挂" + n("线缕") + "。" + n("奇异旅程") + "：普攻时敌方英雄贴身，"
                  "开门造成" + mag("w_dmg", "w_ratio") + "魔法伤害，" + cc("放逐") + t("{w_t}秒") + "后" + cc("减速") + "{w_slow}%" +
                  t("{w_slow_t}秒") + "（每" + t("{w_cd}秒") + "）。",
        "skill": "蓄力后射出回忆魔法弹，自己后退一步：落点周围敌人受到" + mag("q_dmg", "q_ratio") + "魔法伤害，英雄挂上" + n("线缕") +
                 "；那里有琐物时一并引爆，附近的敌方英雄再受琐物伤害。",
        "skill2": "在目标两侧打开两扇门，" + t("{e_delay}秒") + "后线缕穿过：范围内敌人受到" + mag("e_dmg", "e_ratio") + "魔法伤害并挂上" +
                  n("线缕") + "：" + t("{t_t}秒") + "内体型变大{t_size}%（更容易被命中），" + cc("减速") + "{t_slow}%" + t("{t_slow_t}秒") + "。",
        "ult": "在敌方英雄脚下展开大裂隙，每" + t("{r_gap}秒") + "一波毛线球横穿，共4波：裂隙里的敌方英雄每波受到" + mag("r_dmg", "r_ratio") +
               "魔法伤害并" + cc("减速") + "{r_slow}%" + t("{r_slow_t}秒") + "，第4波伤害+{r_last}%。",
        "names": ("回忆涌现", "思乡线缕", "传送门欢腾！"),
    },
    "zh-hant": {
        "name": "諾拉",
        "attack": "星光彈造成" + AD + n("物理傷害") + "。" + n("心愛飾品") + "：每" + t("{p_cd}秒") + "，下個技能落點留下飾品" + t("{p_life}秒") +
                  "，走進的敵方英雄受到" + mag("p_dmg", "p_ratio") + "魔法傷害並掛" + n("絲線") + "。" + n("茫然旅程") + "：普攻時敵方英雄貼身，"
                  "開門造成" + mag("w_dmg", "w_ratio") + "魔法傷害，" + cc("放逐") + t("{w_t}秒") + "後" + cc("緩速") + "{w_slow}%" +
                  t("{w_slow_t}秒") + "（每" + t("{w_cd}秒") + "）。",
        "skill": "蓄力後射出記憶魔法彈，自己後退一步：落點周圍敵人受到" + mag("q_dmg", "q_ratio") + "魔法傷害，英雄掛上" + n("絲線") +
                 "；那裡有飾品時一併引爆，附近的敵方英雄再受飾品傷害。",
        "skill2": "在目標兩側打開兩扇門，" + t("{e_delay}秒") + "後絲線穿過：範圍內敵人受到" + mag("e_dmg", "e_ratio") + "魔法傷害並掛上" +
                  n("絲線") + "：" + t("{t_t}秒") + "內體型變大{t_size}%（更容易被命中），" + cc("緩速") + "{t_slow}%" + t("{t_slow_t}秒") + "。",
        "ult": "在敵方英雄腳下展開大裂隙，每" + t("{r_gap}秒") + "一波毛線球橫穿，共4波：裂隙裡的敵方英雄每波受到" + mag("r_dmg", "r_ratio") +
               "魔法傷害並" + cc("緩速") + "{r_slow}%" + t("{r_slow_t}秒") + "，第4波傷害+{r_last}%。",
        "names": ("記憶湧現", "返家絲線", "傳送門嘉年華！"),
    },
    "en": {
        "name": "Norra",
        "attack": "Star bolt: " + AD + " " + n("physical damage") + ". " + n("Beloved Trinkets") + ": every " + t("{p_cd}s") +
                  " her next ability leaves trinkets where it lands (" + t("{p_life}s") + "): enemy champions walking in take " +
                  mag("p_dmg", "p_ratio") + " " + M + "magic damage" + E + " and the " + n("Threads") + ". " + n("Journey to Nowhere") +
                  ": an enemy champion close as she attacks takes " + mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ", " +
                  cc("banished") + " " + t("{w_t}s") + ", then " + cc("slowed") + " {w_slow}% " + t("{w_slow_t}s") + " (every " +
                  t("{w_cd}s") + ").",
        "skill": "Charges, then flings a bolt of memories and hops back: enemies around where it lands take " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ", champions get the " + n("Threads") + ". Trinkets lying "
                 "there burst too: enemy champions near the blast take their damage.",
        "skill2": "Opens two portals beside the target; " + t("{e_delay}s") + " later threads shoot between them: enemies there take " +
                  mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and get the " + n("Threads") + ": {t_size}% bigger (easier "
                  "to hit) for " + t("{t_t}s") + " and " + cc("slowed") + " {t_slow}% for " + t("{t_slow_t}s") + ".",
        "ult": "Opens a great rift under an enemy champion: 4 volleys of yarn balls cross it " + t("{r_gap}s") + " apart, each "
               "hitting the enemy champions inside for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + " and " +
               cc("slowing") + " them {r_slow}% for " + t("{r_slow_t}s") + "; the 4th deals {r_last}% more.",
        "names": ("Memory Surge", "Threads of Homecoming", "Portalpalooza!"),
    },
    "ko": {
        "name": "노라",
        "attack": "별빛 탄환으로 " + AD + " 물리 피해. " + n("소중한 장신구") + ": " + t("{p_cd}초") + "마다 다음 스킬이 떨어진 곳에 장신구를 " +
                  t("{p_life}초") + " 남김: 들어온 적 챔피언은 " + mag("p_dmg", "p_ratio") + " 마법 피해와 " + n("실타래") + ". " +
                  n("미지로의 여정") + ": 공격 시 적 챔피언이 붙어 있으면 차원문: " + mag("w_dmg", "w_ratio") + " 마법 피해, " +
                  t("{w_t}초") + " " + cc("추방") + " 뒤 " + t("{w_slow_t}초") + " {w_slow}% " + cc("둔화") + "(" + t("{w_cd}초") + "마다).",
        "skill": "충전 후 기억의 탄환을 날리고 뒤로 물러난다: 떨어진 곳 주변 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해, 챔피언에게 " +
                 n("실타래") + ". 그곳의 장신구도 터져 근처 적 챔피언이 장신구 피해를 받는다.",
        "skill2": "대상 양옆에 차원문 두 개를 열고 " + t("{e_delay}초") + " 뒤 실타래가 지나간다: 범위의 적에게 " + mag("e_dmg", "e_ratio") +
                  " 마법 피해와 " + n("실타래") + ": " + t("{t_t}초") + " 동안 {t_size}% 커지고(맞히기 쉬움) " + t("{t_slow_t}초") +
                  " 동안 {t_slow}% " + cc("둔화") + ".",
        "ult": "적 챔피언 발밑에 큰 균열을 열고 " + t("{r_gap}초") + "마다 털실 뭉치가 4번 가로지른다: 매번 안의 적 챔피언에게 " +
               mag("r_dmg", "r_ratio") + " 마법 피해와 " + t("{r_slow_t}초") + " {r_slow}% " + cc("둔화") + ", 4번째는 피해 +{r_last}%.",
        "names": ("밀려드는 기억", "귀향의 실타래", "차원문 대소동!"),
    },
    "ja": {
        "name": "ノラ",
        "attack": "星の弾で" + AD + "の物理ダメージ。" + n("愛用のトリンケット") + "：" + t("{p_cd}秒") + "毎、次スキルの着弾点に" +
                  t("{p_life}秒") + "残り、入った敵チャンピオンに" + mag("p_dmg", "p_ratio") + "魔法ダメージと" + n("スレッド") + "。" +
                  n("どこでもない場所へ") + "：攻撃時に密着した敵に" + mag("w_dmg", "w_ratio") + "魔法ダメージ、" +
                  t("{w_t}秒") + cc("追放") + "後" + t("{w_slow_t}秒") + "{w_slow}%" + cc("スロウ") + "（" + t("{w_cd}秒") + "毎）。",
        "skill": "溜めてから記憶の弾を放ち、後ろへ跳ぶ：着弾点の周りの敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ、チャンピオンに" +
                 n("スレッド") + "。そこのトリンケットも弾け、近くの敵チャンピオンにそのダメージ。",
        "skill2": "対象の両脇に2つのポータルを開き、" + t("{e_delay}秒") + "後にスレッドが走る：範囲の敵に" + mag("e_dmg", "e_ratio") +
                  "の魔法ダメージと" + n("スレッド") + "：" + t("{t_t}秒") + "間{t_size}%大きく（当たりやすい）、" + t("{t_slow_t}秒") +
                  "間{t_slow}%" + cc("スロウ") + "。",
        "ult": "敵チャンピオンの足元に大きな裂け目を開き、" + t("{r_gap}秒") + "毎に毛糸玉が4回横切る：毎回中の敵チャンピオンに" +
               mag("r_dmg", "r_ratio") + "の魔法ダメージと" + t("{r_slow_t}秒") + "{r_slow}%" + cc("スロウ") + "、4回目は+{r_last}%。",
        "names": ("記憶の波動", "帰郷のスレッド", "ポータルパルーザ！"),
    },
}

# sound event -> [(our clip, volume, delay)]: every event the kit plays (build_norra's sfx / tsfx)
SOUNDS = {
    f"{ID}_a": [(CLIP + "a", 0.4, 0.0)],
    f"{ID}_a_hit": [(CLIP + "a_hit", 0.35, 0.0)],
    f"{ID}_p_drop": [(CLIP + "p_drop", 0.35, 0.0)],
    f"{ID}_p_burst": [(CLIP + "p_burst", 0.4, 0.0)],
    f"{ID}_w": [(CLIP + "w", 0.45, 0.0)],
    f"{ID}_q": [(CLIP + "q", 0.35, 0.0)],
    f"{ID}_q_fire": [(CLIP + "q_fire", 0.45, 0.0)],
    f"{ID}_q_blast": [(CLIP + "q_blast", 0.5, 0.0)],
    f"{ID}_e": [(CLIP + "e", 0.45, 0.0)],
    f"{ID}_e_hit": [(CLIP + "e_hit", 0.4, 0.0)],
    f"{ID}_r": [(CLIP + "r", 0.5, 0.0)],
    f"{ID}_r_open": [(CLIP + "r_open", 0.5, 0.0)],
    f"{ID}_r_ball": [(CLIP + "r_ball", 0.4, 0.0)],
    f"{ID}_r_hit": [(CLIP + "r_hit", 0.35, 0.0)],
}


def secs(x):
    return f"{x / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "w_dmg", "w_ratio", "w_slow", "q_dmg", "q_ratio", "e_dmg", "e_ratio",
                           "t_size", "t_slow", "r_dmg", "r_ratio", "r_slow", "r_last")}
    for k in ("p_cd", "p_life", "w_cd", "w_t", "w_slow_t", "e_delay", "t_t", "t_slow_t", "r_gap", "r_slow_t"):
        v[k] = secs(p[k])
    v["q_bonus"] = f"{p['q_bonus'] / 10:g}"           # tenths of a % (the add-on's)
    return v


def shown_length(s):
    return pack.shown_length(s)


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def texts(p):
    v = values(p)
    out = {}
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
    return out


def kit_sounds():
    """Every Sfx / TargetSfx name the kit plays."""
    kit = load(os.path.join(MOD, "champion", f"{ID}.data_champion"))
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(kit)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(x > TOOLTIP_MAX[lang] for x in lens.values())
        print(lang, " ".join(f"{k}:{x}/{TOOLTIP_MAX[lang]}" for k, x in lens.items()))
    if a.check:
        sys.stdout.reconfigure(encoding="utf-8")
        for lang, (d, _) in tx.items():
            for k in ("attack", "skill", "skill2", "ult"):
                print(lang, k, re.sub(r"<[^>]*>", "", d[k]))
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")

    played = kit_sounds()
    if played != set(SOUNDS):
        sys.exit(f"the kit plays {sorted(played - set(SOUNDS))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(SOUNDS) - played)}")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[ID] = d
        i18n[lang].setdefault("skill_name", {})[ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    clips = set()
    for name, plays in SOUNDS.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ".wav"))):
                print(f"warning: {c}.wav missing - run tools/lol/extract_norra.py")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{ID}_")]:   # her sound keys rebuilt
        del ov[k]
    for name in list(SOUNDS) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][ID] = json.loads(json.dumps(VIEW))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi["description"] = pack.DESC.format(heroes=", ".join(pack.HEROES))
    mi["last_updated"] = "2026-10-26"
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print(len(SOUNDS), "sounds,", len(clips), "clips; text, champion_view, mod_info", mi["version"], "written")


if __name__ == "__main__":
    main()
