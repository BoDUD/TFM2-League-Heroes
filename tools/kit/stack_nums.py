"""Stack counts drawn over the heroes' heads: league.dll counts, the heroes' data draws (2026-11-11).

    python tools/kit/stack_nums.py --write   # the number sheet, every listed hero's view_buffs (league/ and the
                                             # add-ons' copies) and league.dll's table addons/league_main/src/stack_table.rs
    python tools/kit/stack_nums.py --check   # (CI) all of them up to date
    python tools/kit/stack_nums.py --list    # the heroes, their rules and heights

Why (the user, 2026-11-11): 「现在叠层数的技能英雄在游戏里看不到多少层 有没有办法在游戏里能看到？」, then 「办法1吧」 (a number
over the head). The data only asks whether a buff is on a unit (`SwitchByBuff`), so it cannot count a stack: each stack
is one more instance of a buff (league_veigar_p_stack) or the next rung of a ladder (league_aurelionsol_d1..d30), and
the game's display world keeps one entry a buff name (hd_engine's grow_count), so the client cannot count them either.

So league.dll counts in the simulation (src/stacks.rs, every `EVERY` ticks, the same in every run of a match) and keeps
name-only display buffs on the hero, one a digit: `<hero>_sn_<tag>`. The tag names a frame of the shared sheet
league/effects/league_stack_num: `y<Y><slot><digit>` is that digit in its slot - a for a one-digit number, b c for two,
d e f for three - with the number's centre Y game px over the hero's position (a picture is drawn with its frame's
centre on the unit, as the target pips of league_kaisa / league_brand are). Each listed hero's view_buffs binds every
name the counter can put on him to its frame (`apply`), in league/champion/ and in every add-on's copy of him; the kit
scripts' `build = stack_nums.wrap(build)` keep the bindings in a rebuild. Dead heroes show nothing.

Y: the highest pixel of the hero's idle and run frames over his position, grown about his soles by league.dll's SIZES
(dense heroes drawn bigger or smaller) - and for a hero in GROWTH (Cho'Gath's Feast) by his growth at that count, so the
number rides on top of him - plus `GAP`.
"""
import argparse
import functools
import glob
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAGUE = os.path.join(ROOT, "league")
SHEET = os.path.join(LEAGUE, "effects", "league_stack_num")
ANIM = "asset/league/effects/league_stack_num"
TABLE_RS = os.path.join(ROOT, "addons", "league_main", "src", "stack_table.rs")
HD_RS = os.path.join(ROOT, "addons", "league_main", "src", "hd.rs")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))

# ---------------------------------------------------------------------------------------------------------------- table
# hero -> how to read the number from his own buffs:
#   count:  the instances of one buff (a stack is one more instance)
#   sum:    one stat of those instances added up, when a stack is not always one (Veigar's champion stack is 5 ability
#           power: League counts it 5 stacks, the number is his ability power from it; Nasus's Siphoning Strike damage;
#           Sion's health from kills) - "stat" names the field (magic_power / hp / attack)
#   ladder: the highest k with <prefix><k> on him, k = 1..rungs, times "step" (default 1: Rumble's heat and Gnar's /
#           Shyvana's rage 10 a rung, Tryndamere's fury 20 - League's 0..100); with "full" (a flag buff: Darius's Noxian
#           Might, Gnar's full Rage) on him, the number is "top"
# cap: the most the number shows (also how many digits it can have); label: what the number is (for --list and the docs)
STACKS = [
    {"hero": "league_veigar", "sum": "league_veigar_p_stack", "stat": "magic_power", "cap": 999,
     "label": "维迦「超凡邪力」叠的法术强度（英雄联盟的层数）"},
    {"hero": "league_nasus", "sum": "league_nasus_q_stack", "stat": "magic_power", "cap": 999,
     "label": "内瑟斯「汲魂痛击」叠的伤害（英雄联盟的层数）"},
    {"hero": "league_chogath", "count": "league_chogath_r_stack", "cap": 99, "label": "科加斯「盛宴」层数"},
    {"hero": "league_smolder", "count": "league_smolder_p_st", "cap": 999, "label": "斯莫德「龙之研习」层数"},
    {"hero": "league_senna", "count": "league_senna_mist", "cap": 999, "label": "赛娜「赦除」黑雾层数"},
    {"hero": "league_swain", "count": "league_swain_frag", "cap": 999, "label": "斯维因「灵魂碎片」"},
    {"hero": "league_sion", "sum": "league_sion_k_hp", "stat": "hp", "cap": 999, "label": "赛恩「灵魂熔炉」击杀加的生命"},
    {"hero": "league_kindred", "count": "league_kindred_p_mark", "cap": 99, "label": "千珏「千珏之印」印记"},
    {"hero": "league_aurelionsol", "ladder": "league_aurelionsol_d", "rungs": 30, "cap": 30,
     "label": "奥瑞利安·索尔「星海焕然」星尘层数"},
    {"hero": "league_belveth", "ladder": "league_belveth_l", "rungs": 8, "cap": 8,
     "label": "卑尔维斯「溶烛化紫」永久攻速层数"},
    # the capped counters League shows that had no picture, or one only when full (the user, 2026-11-11: 「加常见的那些」)
    {"hero": "league_caitlyn", "ladder": "league_caitlyn_hs_", "rungs": 5, "cap": 5,
     "label": "凯特琳「爆头」计数（第 6 发爆头）"},
    {"hero": "league_darius", "ladder": "league_darius_hemo_", "rungs": 4, "full": "league_darius_might", "top": 5,
     "cap": 5, "label": "德莱厄斯「出血」层数（5 = 诺克萨斯之力）"},
    {"hero": "league_pantheon", "ladder": "league_pantheon_m", "rungs": 4, "full": "league_pantheon_pw", "top": 5,
     "cap": 5, "label": "潘森「矢志不退」层数（5 = 下一个技能强化）"},
    {"hero": "league_kennen", "ladder": "league_kennen_a_", "rungs": 4, "cap": 4, "label": "凯南「电刃」普攻计数（第 5 下）"},
    {"hero": "league_jinx", "ladder": "league_jinx_revup_", "rungs": 3, "cap": 3, "label": "金克丝「砰砰」攻速层数"},
    {"hero": "league_masteryi", "ladder": "league_masteryi_ds_", "rungs": 3, "cap": 3, "label": "易「双重打击」计数"},
    {"hero": "league_twistedfate", "ladder": "league_twistedfate_e", "rungs": 3, "cap": 3,
     "label": "崔斯特「卡牌骗术」计数（第 4 下）"},
    {"hero": "league_rumble", "ladder": "league_rumble_h", "rungs": 9, "step": 10, "full": "league_rumble_oh", "top": 100,
     "cap": 100, "label": "兰博「机械重组」热量（100 = 过热）"},
    {"hero": "league_annie", "ladder": "league_annie_pyro_", "rungs": 3, "full": "league_annie_pyro_ready", "top": 4,
     "cap": 4, "label": "安妮「嗜火」层数（4 = 下一个技能晕人）"},
    {"hero": "league_irelia", "ladder": "league_irelia_pv", "rungs": 4, "cap": 4, "label": "艾瑞莉娅「艾欧尼亚热诚」层数"},
    {"hero": "league_kayle", "ladder": "league_kayle_zeal", "rungs": 5, "cap": 5, "label": "凯尔「狂热」层数"},
    {"hero": "league_gnar", "ladder": "league_gnar_rg", "rungs": 9, "step": 10, "full": "league_gnar_full", "top": 100,
     "cap": 100, "label": "纳尔「狂怒基因」怒气（100 = 满怒）"},
    {"hero": "league_shyvana", "ladder": "league_shyvana_fy", "rungs": 9, "step": 10, "full": "league_shyvana_full",
     "top": 100, "cap": 100, "label": "希瓦娜「魔龙降世」龙怒（100 = 满）"},
    {"hero": "league_tryndamere", "ladder": "league_tryndamere_f_", "rungs": 5, "step": 20, "cap": 100,
     "label": "泰达米尔「战斗狂怒」怒气"},
]

# the number's centre this many game px over the hero's highest pixel (its frame's outline then sits 2 px over him)
GAP = 5
# Cho'Gath-like growth: a height for each count up to this, then the last one (a bigger number overlaps his top)
GROW_ROWS = 12
# the picture's draw order: over the heroes' own pictures (the target pips use 2)
Z = 6
FILL = (255, 255, 255, 255)
LINE = (20, 16, 30, 255)
GLYPH = {
    "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "001", "010", "010"),
    "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
}
# a slot's glyph: its left column from the number's centre (one digit: a; two: b c; three: d e f; 4 px a digit)
SLOT_X = {"a": -1, "b": -3, "c": 1, "d": -5, "e": -1, "f": 3}
HALF_W = 6          # the frame: x -HALF_W..HALF_W (13 px; the outline of d / f reaches -6 / 6)


def slots(n):
    """n -> [(slot, digit)] the number shows (none for 0)."""
    s = str(n)
    if n <= 0:
        return []
    return list(zip({1: "a", 2: "bc", 3: "def"}[len(s)], (int(c) for c in s)))


def tag(y, slot, digit):
    return f"y{y}{slot}{digit}"


def buff_name(hero, t):
    return f"{hero}_sn_{t}"


# ------------------------------------------------------------------------------------------------------------- heights
def _rust_table(name):
    """hd.rs's `pub const NAME` rows as tuples of their string / number fields."""
    src = open(HD_RS, encoding="utf-8").read()
    m = re.search(r"pub const %s: [^=]+=\s*&?\[(.*?)\];" % name, src, re.S)
    if not m:
        sys.exit(f"no {name} in {os.path.relpath(HD_RS, ROOT)}: update stack_nums.py")
    rows = []
    for row in re.findall(r"\(([^()]*?)\)", m.group(1)):
        fields = [f.strip() for f in row.split(",") if f.strip()]
        rows.append(tuple(f.strip('"') if f.startswith('"') else float(f) for f in fields if not f.startswith("&")))
    return rows


@functools.lru_cache(None)
def sizes():
    return {r[0]: r[1] for r in _rust_table("SIZES")}


@functools.lru_cache(None)
def growth():
    """hero -> (the buff, growth a stack) from hd.rs GROWTH."""
    return {r[0]: (r[1], r[2]) for r in _rust_table("GROWTH")}


def grown(per, stacks, knee=4, tail=0.5):
    """hd_engine's grown(): the body's size at `stacks` stacks of a growth row."""
    return 1.0 + per * (min(stacks, knee) + tail * max(stacks - knee, 0))


@functools.lru_cache(None)
def body(hero):
    """(how high the hero stands over his position, how low his soles are under it): the median of his idle and run
    frames (game px, 1x frames: the dense ones draw the same size). A frame is drawn with its centre on the unit, so a
    picture over the head is a tall frame with its top rows inked (league_gwen's qs pips, league_riven's runes). The
    median, not the highest: Nasus's idle has a staff flourish of 70, Cho'Gath rears from 26 to 51 in his idle and
    runs at 25 - a flourish may cross the number for a moment, a number that high would float off him the rest."""
    stem = os.path.join(LEAGUE, "champions", hero)
    anims = json.load(open(stem + "#anim.fanim", encoding="utf-8"))["anims"]
    sheet = Image.open(stem + "#sheet.png").convert("RGBA")
    tops, feet = [], []
    for name in ("idle", "run"):
        for fr in anims.get(name, {}).get("frames", []):
            d = fr["data"]
            x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
            if w <= 1 or h <= 1:
                continue
            a = np.asarray(sheet.crop((x, y, x + w, y + h)).getchannel("A")) > 0
            rows = np.nonzero(a.any(axis=1))[0]
            if rows.size:
                tops.append(h // 2 - int(rows[0]))
                feet.append(int(rows[-1]) - h // 2)
    if not tops:
        sys.exit(f"{hero}: no idle / run frame to measure")
    return int(np.median(tops)), int(np.median(feet))


def height(hero, scale=1.0):
    """The number's centre over the hero's position, the hero drawn `scale` times his size about his soles."""
    top, feet = body(hero)
    s = sizes().get(hero, 1.0) * scale
    return int(math.ceil((top + feet) * s - feet)) + GAP


def ys(row):
    """The number's height for counts 1, 2, ... (one height, or one a count up to GROW_ROWS for a growing hero)."""
    hero = row["hero"]
    g = growth().get(hero)
    if g and g[0] == row.get("count"):     # the growth counts instances: only a count row grows with it
        return [height(hero, grown(g[1], n)) for n in range(1, GROW_ROWS + 1)]
    return [height(hero)]


def y_for(row_ys, n):
    return row_ys[min(n, len(row_ys)) - 1]


def values(row):
    """Every number the counter can show the hero (a ladder only its rungs' and the full flag's)."""
    if "ladder" in row:
        step = row.get("step", 1)
        out = {k * step for k in range(1, row["rungs"] + 1)} | ({row["top"]} if "full" in row else set())
        return sorted(v for v in out if 1 <= v <= row["cap"])
    return list(range(1, row["cap"] + 1))


def shows(row):
    """Every (Y, slot, digit) the counter can put on the hero."""
    hy = ys(row)
    out = set()
    for n in values(row):
        y = y_for(hy, n)
        out.update((y, s, d) for s, d in slots(n))
    return sorted(out)


# --------------------------------------------------------------------------------------------------------------- sheet
def frame(y, slot, digit):
    """The digit in its slot, the number's centre y px over the frame's centre: a 13 x (2y + 7) frame."""
    h = 2 * (y + 3) + 1
    a = np.zeros((h, 2 * HALF_W + 1, 4), np.uint8)
    ink = np.zeros(a.shape[:2], bool)
    cy, cx = y + 3, HALF_W
    x0 = cx + SLOT_X[slot]
    y0 = cy - y - 2
    for r, row in enumerate(GLYPH[str(digit)]):
        for c, v in enumerate(row):
            if v == "1":
                ink[y0 + r, x0 + c] = True
    line = np.zeros_like(ink)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            line |= np.roll(np.roll(ink, dy, 0), dx, 1)
    a[line & ~ink] = LINE
    a[ink] = FILL
    return a


def sheet_tags():
    """{tag: [(frame, ms)]} for every tag a listed hero can show, in a fixed order."""
    want = sorted({(y, s, d) for row in STACKS for (y, s, d) in shows(row)})
    return {tag(y, s, d): [(frame(y, s, d), 1000)] for y, s, d in want}


def write_sheet():
    import strips  # the skill's sheet packer
    return strips.write_sheet(SHEET, sheet_tags(), share=True)


def sheet_problems():
    try:
        anims = json.load(open(SHEET + "#anim.fanim", encoding="utf-8"))["anims"]
        sheet = np.asarray(Image.open(SHEET + "#sheet.png").convert("RGBA"))
    except OSError as e:
        return [f"no number sheet ({e}): python tools/kit/stack_nums.py --write"]
    want = sheet_tags()
    if set(anims) != set(want):
        return [f"the number sheet's tags differ (missing {sorted(set(want) - set(anims))[:5]}, extra "
                f"{sorted(set(anims) - set(want))[:5]}): python tools/kit/stack_nums.py --write"]
    for t, frames in want.items():
        d = anims[t]["frames"][0]["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        if not np.array_equal(sheet[y:y + h, x:x + w], frames[0][0]):
            return [f"the number sheet's {t} is not the digit it should be: python tools/kit/stack_nums.py --write"]
    return []


# ------------------------------------------------------------------------------------------------------- the views
def views(hero):
    """The view_buffs entries binding every display buff the counter can put on `hero`."""
    row = next((r for r in STACKS if r["hero"] == hero), None)
    if row is None:
        return []
    return [{"type": "Animated", "name": buff_name(hero, tag(y, s, d)), "anim": ANIM, "tag": tag(y, s, d),
             "repeat": True, "z": Z} for y, s, d in shows(row)]


def apply(champ):
    """The champion with its stack-number bindings: any old ones replaced where the first of them stood (an add-on's copy
    keeps its own views after the main pack's, whichever way it was made), else added last; other views keep their order."""
    hero = champ.get("id", "")
    prefix = f"{hero}_sn_"
    old = champ.get("view_buffs", [])
    mine = [i for i, v in enumerate(old) if str(v.get("name", "")).startswith(prefix)]
    at = mine[0] if mine else len(old)
    rest = [v for v in old if not str(v.get("name", "")).startswith(prefix)]
    add = views(hero)
    if add or "view_buffs" in champ:
        champ["view_buffs"] = rest[:at] + add + rest[at:]
    return champ


def wrap(build):
    """`build = stack_nums.wrap(build)` under a kit script's build(): every caller gets the kit with the bindings."""
    @functools.wraps(build)
    def built(*a, **k):
        return apply(build(*a, **k))
    return built


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def copies():
    """Every data file of a listed hero: league/champion/ and the add-ons' override/ copies."""
    heroes = {r["hero"] for r in STACKS}
    files = sorted(glob.glob(os.path.join(LEAGUE, "champion", "*.data_champion")) +
                   glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion")))
    for path in files:
        if os.path.basename(path).split(".")[0] in heroes:
            yield path


def data_problems(write=False):
    out = []
    for path in copies():
        raw = open(path, "rb").read().decode("utf-8")
        champ = json.loads(raw)
        if champ.get("id") != os.path.basename(path).split(".")[0]:
            continue
        new = dumps_main(apply(json.loads(raw)))
        if "\r\n" not in raw:       # the add-ons' make_override.py write LF (git stores LF either way)
            new = new.replace("\r\n", "\n")
        if new.replace("\r\n", "\n") != raw.replace("\r\n", "\n"):
            if write:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
                out.append(f"wrote {os.path.relpath(path, ROOT)}")
            else:
                out.append(f"{os.path.relpath(path, ROOT)}: its stack-number views are not up to date: "
                           "python tools/kit/stack_nums.py --write")
    return out


# ------------------------------------------------------------------------------------------------------- league.dll
STATS = {"magic_power": "MagicPower", "hp": "Hp", "attack": "Attack"}


def rule_rs(r):
    if "count" in r:
        return f'Rule::Count("{r["count"]}")'
    if "sum" in r:
        return f'Rule::Sum("{r["sum"]}", Stat::{STATS[r["stat"]]})'
    full = f'Some(("{r["full"]}", {r["top"]}))' if "full" in r else "None"
    return (f'Rule::Ladder {{ prefix: "{r["ladder"]}", rungs: {r["rungs"]}, step: {r.get("step", 1)}, '
            f'full: {full} }}')


def table_rs():
    lines = ["//! The stack counts league.dll draws over the heroes' heads (src/stacks.rs): generated by",
             "//! tools/kit/stack_nums.py from its STACKS - do not edit by hand.", "",
             "use super::stacks::{Rule, Stack, Stat};", "",
             f"pub const STACKS: [Stack; {len(STACKS)}] = ["]
    for r in sorted(STACKS, key=lambda r: r["hero"]):
        rule = rule_rs(r)
        lines.append(f'    Stack {{ hero: "{r["hero"]}", rule: {rule}, cap: {r["cap"]}, ys: &{ys(r)} }},')
    lines += ["];", ""]
    return "\n".join(lines)


def table_problems():
    have = open(TABLE_RS, encoding="utf-8").read().replace("\r\n", "\n") if os.path.exists(TABLE_RS) else ""
    if have != table_rs():
        return [f"{os.path.relpath(TABLE_RS, ROOT)} is out of date: python tools/kit/stack_nums.py --write"]
    return []


def rules_problems():
    """Every counted buff / ladder rung exists in the hero's own data (a renamed buff would count nothing)."""
    out = []
    for r in STACKS:
        raw = open(os.path.join(LEAGUE, "champion", r["hero"] + ".data_champion"), encoding="utf-8").read()
        names = ([r["count"]] if "count" in r else [r["sum"]] if "sum" in r else
                 [f'{r["ladder"]}{k}' for k in (1, r["rungs"])] + ([r["full"]] if "full" in r else []))
        if "sum" in r and f'"{r["stat"]}"' not in raw:
            out.append(f"{r['hero']}: no buff of it carries {r['stat']}")
        for n in names:
            if f'"{n}"' not in raw:
                out.append(f"{r['hero']}: {n} is not in its data")
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for r in STACKS:
            what = r.get("count") or (f'{r["sum"]} {r["stat"]}' if "sum" in r else f'{r["ladder"]}1..{r["rungs"]}')
            hy = ys(r)
            print(f'{r["hero"]:22s} {what:34s} cap {r["cap"]:4d}  y {hy[0] if len(hy) == 1 else hy}  {r["label"]}')
    if a.write:
        w, h = write_sheet()
        print(f"wrote {os.path.relpath(SHEET, ROOT)}#sheet.png ({w}x{h}, {len(sheet_tags())} tags)")
        with open(TABLE_RS, "w", encoding="utf-8", newline="\n") as f:
            f.write(table_rs())
        print("wrote", os.path.relpath(TABLE_RS, ROOT))
        for line in data_problems(write=True):
            print(line)
    if a.check:
        bad = rules_problems() + sheet_problems() + table_problems() + data_problems()
        for b in bad:
            print(b)
        if bad:
            sys.exit(f"{len(bad)} problem(s)")
        print(f"stack numbers: {len(STACKS)} heroes, sheet / views / league.dll table up to date")


if __name__ == "__main__":
    main()
