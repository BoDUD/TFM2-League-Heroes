//! 屏幕上的彩蛋：任务的大字公告、小一号的提示，和比赛下方玩家栏里英雄头像上的计数（警察抓小偷的「抓捕的罪犯」「甩掉的条子」、
//! 锤石 / 赛娜 / 卢锡安的灵魂层数）和冰雪女王的小冠冕。
//!
//! 彩蛋在模拟里跑（`lib.rs` 的比赛钩子）；屏幕放的是跑在前面的模拟的回放（league_akshan banner.rs 的做法）：屏幕上那一场
//! （`ClientMatchView`、观战、回放）里发生时记下 (场次, 局, tick, 内容)，按屏幕上的比赛时钟（`game_places::clock::screen_tick`，
//! 附加包合集里由佛耶戈的时钟读取器喂，单独装时由本包的 [`Overlay`] 喂）到了那一 tick 才画。几条挤在一起时排队，一条接一条
//! （[`schedule`]）。文字按游戏的语言（简体、繁体，其他语言用英文），英雄名按游戏自己的文字。
//!
//! 游戏每个 mod 只有一个客户端扩展槽：附加包合集里由 league_addons 的 `BundleClient` 调 [`draw`]，单独的 league_eggs.dll 用
//! [`Overlay`]。英雄头像上没有办法画跟着英雄走的图（客户端画不到对局里的实体），所以计数画在玩家栏上（league_ornn 锻造光晕的做法：
//! `ingame.player_info` / `ingame.wide_data.player_info` 下每行一条分路，`blue_player` 是 0 队）。

use std::sync::Mutex;

use mod_api_stable::*;

/// 大字（宿命对决的开始和结果）停多久、小提示停多久（tick，60 一秒）、最后多久淡出。
pub const BIG_T: usize = 240;
pub const SMALL_T: usize = 180;
pub const FADE_T: usize = 40;
/// 玩家栏的两种布局（普通、宽屏），行里的两边、各是哪一队（league_ornn fx.rs）。
pub const PANELS: [&str; 2] = ["ingame.player_info", "ingame.wide_data.player_info"];
pub const SIDES: [(&str, usize); 2] = [("blue_player", 0), ("red_player", 1)];

const UI: &str = "UI";
const FONT: &str = "asset/base/font/set/regular";

/// 一条公告的内容：英雄都是英雄 id（`league_jinx`），画的时候换成游戏里的名字。
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum What {
    HuntStart { rengar: String, khazix: String },
    HuntWon { winner: String, loser: String },
    QueensStart { queens: Vec<String> },
    Queen { queen: String },
    CopsStart { cops: Vec<String>, robbers: Vec<String> },
    Caught { cop: String, n: usize },
    Escaped { robber: String, n: usize },
    FishStart { thresh: Vec<String>, others: Vec<String> },
    SoulTaken { thresh: String, senna: String, n: usize },
    SoulsFreed { by: String, thresh: String, n: usize },
    BearsStart { zilean: String, volibear: String },
    BearBounty { killer: String, victim: String },
    ZombieBounty { killer: String, victim: String },
    Plants { zyra: String, maokai: String },
    Ninjas { ninjas: Vec<String>, hp: i32 },
    Charm { nidalee: String, allies: Vec<String> },
    // ---- 0.2.0（用户 2026-11-09：「我需要所有彩蛋都要有提示 你看看哪些没有的补进去」）：玩法在主包的数据、别的附加包或
    // shades_shark.rs 里，本包从 buff、击杀记录、阵容里认出来放提示（都是小提示）
    /// 1 雷恩加尔 / 卡兹克第一次看见对方（他们数据里的愤怒标记和台词，一局一条）。
    HuntSighted { seer: String, seen: String },
    /// 1 的奖励：雷恩加尔击杀卡兹克的战利品、卡兹克击杀雷恩加尔的额外进化（攻击力 +pct%，每条命一次）。
    Trophy { rengar: String, khazix: String, pct: i32 },
    Evolved { khazix: String, rengar: String, pct: i32 },
    /// 6 太阳镜防晒：一个戴墨镜的人第一次挂上墨镜（每人一局一条）。
    Shades { wearer: String, leona: String },
    /// 7 光合作用：蕾欧娜的阳光第一次让婕拉的植物变大（league_zyra，一局一条）。
    Sunlit { leona: String, zyra: String },
    /// 9 鲨鱼吃小矮子：每吞掉一具。
    Swallowed { fizz: String, yordle: String },
    /// 10 蛇女不需要鞋：开局。
    Barefoot { cassiopeia: String },
    /// 霞洛联动：开局；洛第一次分到霞的 W；洛的 E 第一次落在霞身上（各一局一条）。
    DuoStart { xayah: String, rakan: String },
    DuoW { rakan: String, xayah: String },
    DuoE { rakan: String, xayah: String },
}

impl What {
    /// 宿命对决（一）的公告是大字，其余是小提示。
    pub fn big(&self) -> bool {
        matches!(
            self,
            What::HuntStart { .. }
                | What::HuntWon { .. }
                | What::QueensStart { .. }
                | What::Queen { .. }
                | What::CopsStart { .. }
                | What::FishStart { .. }
                | What::BearsStart { .. }
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Note {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub what: What,
}

/// 玩家栏头像上的东西。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum BadgeKind {
    /// 凯特琳 / 蔚：抓捕的罪犯。
    Arrests,
    /// 金克丝：甩掉的条子。
    Escapes,
    /// 锤石：吸收的灵魂。
    Souls,
    /// 赛娜 / 卢锡安：解放的灵魂。
    Freed,
    /// 弗雷尔卓德的女王。
    Crown,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Badge {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub team: usize,
    pub lane: usize,
    pub kind: BadgeKind,
    pub value: usize,
}

pub(crate) static NOTES: Mutex<Vec<Note>> = Mutex::new(Vec::new());
pub(crate) static BADGES: Mutex<Vec<Badge>> = Mutex::new(Vec::new());
/// 屏幕看的那一场（最近一个屏幕模拟）。
static VIEW: Mutex<Option<(u64, u64)>> = Mutex::new(None);
/// 画过的公告（场次, 局, 开始的 tick, 第几条）和头像计数（场次, 局, 队伍, 分路, 种类, 数）：各记一行日志。
static DRAWN: Mutex<Vec<(u64, u64, usize, usize)>> = Mutex::new(Vec::new());
static BADGED: Mutex<Vec<(u64, u64, usize, usize, BadgeKind, usize)>> = Mutex::new(Vec::new());

/// 屏幕在放这一场（比赛钩子在每个屏幕模拟里记）：只留这一场的公告和计数，换了一场记一行 `VIEW`。
pub fn note_view(m: u64, s: u64) {
    let Ok(mut v) = VIEW.lock() else { return };
    if *v == Some((m, s)) {
        return;
    }
    let was = v.map_or("none".to_string(), |(m, s)| format!("m={m} s={s}"));
    *v = Some((m, s));
    drop(v);
    if let Ok(mut n) = NOTES.lock() {
        n.retain(|x| (x.m, x.s) == (m, s));
    }
    if let Ok(mut b) = BADGES.lock() {
        b.retain(|x| (x.m, x.s) == (m, s));
    }
    if let Some(k) = super::counted("view") {
        super::wlog(format!("VIEW m={m} s={s} on screen (was {was}) #{k}"));
    }
}

/// 屏幕模拟里发生了一件（同一场再放一遍时同样的一条不再记）。
pub fn note(n: Note) {
    if let Ok(mut l) = NOTES.lock() {
        if !l.contains(&n) {
            l.push(n);
        }
    }
}

pub fn badge(b: Badge) {
    if let Ok(mut l) = BADGES.lock() {
        if !l.contains(&b) {
            l.push(b);
        }
    }
}

/// 一条道（大字或小提示）上的公告排队：按发生的 tick，前一条没放完的往后排。-> (开始的 tick, 那一条)
pub fn schedule<'a>(notes: &[&'a Note], show: usize) -> Vec<(usize, &'a Note)> {
    let mut v: Vec<&Note> = notes.to_vec();
    v.sort_by_key(|n| n.tick); // stable: the same tick keeps the order they came in
    let mut end = 0;
    v.into_iter()
        .map(|n| {
            let start = n.tick.max(end);
            end = start + show;
            (start, n)
        })
        .collect()
}

/// 屏幕时钟 `t` 时这条道上在放的那条：(第几条, 那一条, 放了几 tick)。
pub fn showing<'a>(all: &'a [Note], view: Option<(u64, u64)>, big: bool, t: usize) -> Option<(usize, &'a Note, usize)> {
    let (m, s) = view?;
    let mine: Vec<&Note> = all.iter().filter(|n| (n.m, n.s) == (m, s) && n.what.big() == big).collect();
    let show = if big { BIG_T } else { SMALL_T };
    schedule(&mine, show)
        .into_iter()
        .enumerate()
        .find(|(_, (start, _))| *start <= t && t < start + show)
        .map(|(i, (start, n))| (i, n, t - start))
}

/// 屏幕时钟 `t` 时一个选手头像上这一种计数（tick ≤ t 的最后一条；0 不画）。
pub fn badge_at(all: &[Badge], view: Option<(u64, u64)>, team: usize, lane: usize, kind: BadgeKind, t: usize) -> Option<usize> {
    let (m, s) = view?;
    all.iter()
        .filter(|b| (b.m, b.s) == (m, s) && b.team == team && b.lane == lane && b.kind == kind && b.tick <= t)
        .max_by_key(|b| b.tick)
        .map(|b| b.value)
        .filter(|&v| v > 0)
}

/// 淡入淡出：前 10 tick 升上来，最后 FADE_T tick 线性降到 0。
pub fn alpha(age: usize, show: usize) -> u32 {
    let left = show.saturating_sub(age);
    let a = if left >= FADE_T { 255 } else { 255 * left / FADE_T };
    (a.min(255 * (age + 1) / 10)).min(255) as u32
}

/// 游戏的语言（按阿克尚第一个技能名的写法认，league_akshan banner.rs）：简体、繁体，其他都用英文。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lang {
    Hans,
    Hant,
    En,
}

pub fn lang_of(skill1: &str) -> Lang {
    let has = |lo: u32, hi: u32| skill1.chars().any(|c| (lo..=hi).contains(&(c as u32)));
    if has(0xac00, 0xd7a3) || has(0x3040, 0x30ff) {
        Lang::En
    } else if skill1.contains('復') || skill1.contains('還') {
        Lang::Hant
    } else if has(0x4e00, 0x9fff) {
        Lang::Hans
    } else {
        Lang::En
    }
}

/// 几个名字并列。
pub fn join(lang: Lang, names: &[String]) -> String {
    names.join(if lang == Lang::En { ", " } else { "、" })
}

/// 6 太阳镜防晒：戴的是什么（简体、繁体、英文；`rules::SUNGLASSES` 挑的时候看的图）：薇恩、洛克的墨镜，黑默丁格、吉格斯的护目镜，
/// 图奇的目镜，李青的蒙眼布。
pub fn eyewear(id: &str) -> (&'static str, &'static str, &'static str) {
    match id {
        "league_heimerdinger" | "league_ziggs" => ("护目镜", "護目鏡", "goggles"),
        "league_twitch" => ("目镜", "目鏡", "eyepieces"),
        "league_leesin" => ("蒙眼布", "矇眼布", "a blindfold"),
        _ => ("墨镜", "墨鏡", "sunglasses"),
    }
}

/// 一条公告的字：(标题, 第二行)。`name` 把英雄 id 换成名字。
pub fn words(lang: Lang, what: &What, name: &dyn Fn(&str) -> String) -> (String, String) {
    let names = |v: &[String]| join(lang, &v.iter().map(|x| name(x)).collect::<Vec<_>>());
    let (hans, hant, en): (String, String, String);
    match what {
        What::HuntStart { rengar, khazix } => {
            let (r, k) = (name(rengar), name(khazix));
            hans = format!("狩猎开始！|{r} 与 {k} 的宿命对决：先击杀或助攻击杀对方者获胜");
            hant = format!("狩獵開始！|{r} 與 {k} 的宿命對決：先擊殺或助攻擊殺對方者獲勝");
            en = format!("The Hunt Is On!|{r} vs {k}: the first to take the other down wins");
        }
        What::HuntWon { winner, loser } => {
            let (w, l) = (name(winner), name(loser));
            hans = format!("狩猎结束！|{w} 猎杀了 {l}");
            hant = format!("狩獵結束！|{w} 獵殺了 {l}");
            en = format!("The Hunt Is Over!|{w} has hunted down {l}");
        }
        What::QueensStart { queens } => {
            let q = names(queens);
            hans = format!("弗雷尔卓德之战！|{q}：谁会成为弗雷尔卓德的女王？");
            hant = format!("弗雷爾卓德之戰！|{q}：誰會成為弗雷爾卓德的女王？");
            en = format!("War for the Freljord!|{q}: who will be the Queen of the Freljord?");
        }
        What::Queen { queen } => {
            let q = name(queen);
            hans = format!("弗雷尔卓德的女王|{q} 戴上了寒冰王冠！");
            hant = format!("弗雷爾卓德的女王|{q} 戴上了寒冰王冠！");
            en = format!("Queen of the Freljord|{q} wears the ice crown!");
        }
        What::CopsStart { cops, robbers } => {
            let (c, r) = (names(cops), names(robbers));
            hans = format!("警察抓小偷！|{c} 追捕 {r}：每次击杀或助攻对方 +1 金币");
            hant = format!("警察抓小偷！|{c} 追捕 {r}：每次擊殺或助攻對方 +1 金幣");
            en = format!("Cops and Robbers!|{c} vs {r}: +1 gold for every takedown of the other side");
        }
        What::Caught { cop, n } => {
            let c = name(cop);
            hans = format!("{c} 抓捕的罪犯：{n}（+1 金币）|");
            hant = format!("{c} 抓捕的罪犯：{n}（+1 金幣）|");
            en = format!("{c}: criminals caught {n} (+1 gold)|");
        }
        What::Escaped { robber, n } => {
            let r = name(robber);
            hans = format!("{r} 甩掉的条子：{n}（+1 金币）|");
            hant = format!("{r} 甩掉的條子：{n}（+1 金幣）|");
            en = format!("{r}: cops shaken off {n} (+1 gold)|");
        }
        What::FishStart { thresh, others } => {
            let (t, o) = (names(thresh), names(others));
            hans = format!("钓鱼执法！|{t} 的灯笼盯上了 {o} 的灵魂");
            hant = format!("釣魚執法！|{t} 的燈籠盯上了 {o} 的靈魂");
            en = format!("Fishing for Souls!|{t}'s lantern hungers for {o}'s soul");
        }
        What::SoulTaken { thresh, senna, n } => {
            let (t, s) = (name(thresh), name(senna));
            hans = format!("{t} 吸收了 {s} 的灵魂！护甲、法强提高（{n} 层）|");
            hant = format!("{t} 吸收了 {s} 的靈魂！護甲、法強提高（{n} 層）|");
            en = format!("{t} absorbed {s}'s soul! More armor and ability power ({n})|");
        }
        What::SoulsFreed { by, thresh, n } => {
            let (b, t) = (name(by), name(thresh));
            hans = format!("{b} 解放了 {t} 灯笼里的灵魂！暴击、射程提高（{n} 层）|");
            hant = format!("{b} 解放了 {t} 燈籠裡的靈魂！暴擊、射程提高（{n} 層）|");
            en = format!("{b} freed the souls in {t}'s lantern! More crit and range ({n})|");
        }
        What::BearsStart { zilean, volibear } => {
            let (z, v) = (name(zilean), name(volibear));
            hans = format!("时光老头与装甲熊|{z}：装甲熊异见分子　{v}：时光老头的仇恨　击杀对方 +11 金币");
            hant = format!("時光老頭與裝甲熊|{z}：裝甲熊異見分子　{v}：時光老頭的仇恨　擊殺對方 +11 金幣");
            en = format!("The Old Timer and the Armored Bear|{z}: Armored Bear Dissident · {v}: Old Timer's Grudge · +11 gold a kill");
        }
        What::BearBounty { killer, victim } => {
            let (k, v) = (name(killer), name(victim));
            hans = format!("{k} 击杀了 {v}：+11 金币|");
            hant = format!("{k} 擊殺了 {v}：+11 金幣|");
            en = format!("{k} took down {v}: +11 gold|");
        }
        What::ZombieBounty { killer, victim } => {
            let (k, v) = (name(killer), name(victim));
            hans = format!("植物大战僵尸：{k} 击杀了 {v}，+2 金币|");
            hant = format!("植物大戰殭屍：{k} 擊殺了 {v}，+2 金幣|");
            en = format!("Plants vs Zombies: {k} took down {v}, +2 gold|");
        }
        What::Plants { zyra, maokai } => {
            let (z, m) = (name(zyra), name(maokai));
            hans = format!("植物大战僵尸：{z} 和 {m} 结伴同行，移速 +1%|");
            hant = format!("植物大戰殭屍：{z} 和 {m} 結伴同行，移速 +1%|");
            en = format!("Plants vs Zombies: {z} and {m} walk together, +1% move speed|");
        }
        What::Ninjas { ninjas, hp } => {
            let n = names(ninjas);
            hans = format!("忍者的孤独：{n} 同队，各自最大生命 {hp}|");
            hant = format!("忍者的孤獨：{n} 同隊，各自最大生命 {hp}|");
            en = format!("Lonely Ninjas: {n} on one team, {hp} max health each|");
        }
        What::Charm { nidalee, allies } => {
            let (n, a) = (name(nidalee), names(allies));
            hans = format!("熟女的魅力：{n} 带着 {a}，+5 金币|");
            hant = format!("熟女的魅力：{n} 帶著 {a}，+5 金幣|");
            en = format!("Cougar's Charm: {n} brings {a} along, +5 gold|");
        }
        What::HuntSighted { seer, seen } => {
            let (a, b) = (name(seer), name(seen));
            hans = format!("{a} 发现了 {b}！宿敌相见，分外眼红|");
            hant = format!("{a} 發現了 {b}！宿敵相見，分外眼紅|");
            en = format!("{a} has spotted {b}! The rivals meet|");
        }
        What::Trophy { rengar, khazix, pct } => {
            let (r, k) = (name(rengar), name(khazix));
            hans = format!("狩猎战利品：{r} 拿下了 {k} 的头，攻击力 +{pct}%|");
            hant = format!("狩獵戰利品：{r} 拿下了 {k} 的頭，攻擊力 +{pct}%|");
            en = format!("Hunter's Trophy: {r} takes {k}'s head, +{pct}% attack|");
        }
        What::Evolved { khazix, rengar, pct } => {
            let (k, r) = (name(khazix), name(rengar));
            hans = format!("额外进化：{k} 猎杀了 {r}，攻击力 +{pct}%|");
            hant = format!("額外進化：{k} 獵殺了 {r}，攻擊力 +{pct}%|");
            en = format!("Extra Evolution: {k} hunted down {r}, +{pct}% attack|");
        }
        What::Shades { wearer, leona } => {
            let (w, l) = (name(wearer), name(leona));
            let (gs, gt, ge) = eyewear(wearer);
            hans = format!("太阳镜防晒：{w} 戴着{gs}，{l} 的烈阳每层少烧 1%|");
            hant = format!("太陽鏡防曬：{w} 戴著{gt}，{l} 的烈陽每層少燒 1%|");
            en = format!("Sunglasses: {w} wears {ge}, {l}'s Sunlight burns 1% less|");
        }
        What::Sunlit { leona, zyra } => {
            let (l, z) = (name(leona), name(zyra));
            hans = format!("光合作用：{l} 的阳光照在 {z} 的植物上，植物长大了一号|");
            hant = format!("光合作用：{l} 的陽光照在 {z} 的植物上，植物長大了一號|");
            en = format!("Photosynthesis: {l}'s sunlight grows {z}'s plant a size|");
        }
        What::Swallowed { fizz, yordle } => {
            let (f, y) = (name(fizz), name(yordle));
            hans = format!("鲨鱼吃小矮子：{f} 的鲨鱼把 {y} 一口吞了|");
            hant = format!("鯊魚吃小矮子：{f} 的鯊魚把 {y} 一口吞了|");
            en = format!("Shark Snack: {f}'s shark swallowed {y} whole|");
        }
        What::Barefoot { cassiopeia } => {
            let c = name(cassiopeia);
            hans = format!("蛇女不需要鞋：{c} 没有脚，不穿鞋，每升一级移速多涨一点|");
            hant = format!("蛇女不需要鞋：{c} 沒有腳，不穿鞋，每升一級移速多漲一點|");
            en = format!("No Feet, No Boots: {c} gains more move speed every level|");
        }
        What::DuoStart { xayah, rakan } => {
            let (x, r) = (name(xayah), name(rakan));
            hans = format!("霞洛联动：{x} 和 {r} 同队，她的羽衣分他一份，他的舞步飞得更远|");
            hant = format!("情侶聯動：{x} 和 {r} 同隊，她的羽翼分他一份，他的舞步飛得更遠|");
            en = format!("Lovers' Duo: {x} and {r} - shared plumage, a longer dance|");
        }
        What::DuoW { rakan, xayah } => {
            let (r, x) = (name(rakan), name(xayah));
            hans = format!("霞洛联动：{r} 分到了 {x} 的「致死羽衣」，攻速、移速提高|");
            hant = format!("情侶聯動：{r} 分到了 {x} 的「奪命疾翼」，攻速、移速提高|");
            en = format!("Lovers' Duo: {r} shares {x}'s Deadly Plumage|");
        }
        What::DuoE { rakan, xayah } => {
            let (r, x) = (name(rakan), name(xayah));
            hans = format!("霞洛联动：{r} 的「轻舞成双」飞到 {x} 身边，给她一层护盾|");
            hant = format!("情侶聯動：{r} 的「戰鬥舞踊」飛到 {x} 身邊，給她一層護盾|");
            en = format!("Lovers' Duo: {r}'s Battle Dance carries him to {x}'s side|");
        }
    }
    let line = match lang {
        Lang::Hans => hans,
        Lang::Hant => hant,
        Lang::En => en,
    };
    let (a, b) = line.split_once('|').unwrap_or((&line, ""));
    (a.to_string(), b.to_string())
}

/// 游戏的一条文字（league_akshan banner.rs：先带 `#` 查，再不带查，查到空的或原样的键都不算）。
fn text(ctx: &StableClient<'_>, key: &str) -> Option<String> {
    [format!("#{key}"), key.to_string()].into_iter().find_map(|k| ctx.i18n(&k).filter(|s| !s.is_empty() && *s != k))
}

fn hero_name(ctx: &StableClient<'_>, id: &str) -> String {
    text(ctx, &format!("asset/base/text/champion?description.{id}.name"))
        .unwrap_or_else(|| id.trim_start_matches("league_").to_string())
}

/// 节点和它的每一层父节点都显示着（league_ornn fx.rs）。
fn shown(ctx: &StableClient<'_>, path: &str) -> bool {
    let parts: Vec<&str> = path.split('.').collect();
    (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
}

/// 画（客户端扩展的 post_render 里调）：公告和玩家栏上的计数。
pub fn draw(ctx: &mut StableClient<'_>) {
    if !ctx.is_in_game() {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let view = VIEW.lock().ok().and_then(|v| *v);
    let Some((m, s)) = view else { return };
    let Some((w, h)) = ctx.draw_map_size(UI).filter(|s| s.0 > 0.0 && s.1 > 0.0) else { return };
    let lang = lang_of(&text(ctx, "asset/base/text/champion?skill_name.league_akshan.skill1").unwrap_or_default());
    let shows: Vec<(bool, usize, Note, usize)> = {
        let Ok(all) = NOTES.lock() else { return };
        [true, false]
            .into_iter()
            .filter_map(|big| showing(&all, view, big, t).map(|(i, n, age)| (big, i, n.clone(), age)))
            .collect()
    };
    let big_h = (h * 0.055).max(26.0) * 1.5 + (h * 0.026).max(15.0) * 1.7;
    for (big, i, n, age) in shows {
        let name = |id: &str| hero_name(ctx, id);
        let (title, sub) = words(lang, &n.what, &name);
        if let Ok(mut d) = DRAWN.lock() {
            let key = (m, s, n.tick, i + if big { 0 } else { 1 << 20 });
            if !d.contains(&key) {
                d.push(key);
                if d.len() > 512 {
                    d.drain(..256);
                }
                if let Some(k) = super::counted("note") {
                    super::wlog(format!("NOTE m={m} s={s} t={} on screen at {t}: \"{title}\" \"{sub}\" ({lang:?}, UI {w:.0}x{h:.0}) #{k}",
                                        n.tick));
                }
            }
        }
        let show = if big { BIG_T } else { SMALL_T };
        let a = alpha(age, show);
        if big {
            banner(ctx, (w, h), &title, &sub, a, &n.what);
        } else {
            toast(ctx, (w, h), big_h, &title, a);
        }
    }
    badges(ctx, t, view);
}

/// 大字：画面中上方一个框，标题金色（女王的冰蓝），第二行白色。
fn banner(ctx: &mut StableClient<'_>, (w, h): (f32, f32), title: &str, sub: &str, a: u32, what: &What) {
    let size = (h * 0.055).max(26.0);
    let small = (h * 0.026).max(15.0);
    let (bw, bh) = (w * 0.66, size * 1.5 + small * 1.7);
    let (x, y) = ((w - bw) / 2.0, h * 0.16);
    let ice = matches!(what, What::QueensStart { .. } | What::Queen { .. });
    let (edge, gold) = if ice { (0x8f_e4_ff_00, 0xc8_f4_ff_00) } else { (0xf2_c4_4a_00, 0xff_d8_5a_00) };
    ctx.draw_rect(UI, x, y, bw, bh, 910, bh * 0.2, 0x10_14_22_00 | (a * 215 / 255));
    ctx.draw_rect(UI, x, y + bh - 4.0, bw, 4.0, 911, 0.0, edge | a);
    let r = (x, y + size * 0.15, bw, size * 1.3);
    ctx.draw_text(UI, title, FONT, (r.0 + 3.0, r.1 + 3.0, r.2, r.3), 912, size, a, TextAlignXV1::Center, TextAlignYV1::Center);
    ctx.draw_text(UI, title, FONT, r, 913, size, gold | a, TextAlignXV1::Center, TextAlignYV1::Center);
    if !sub.is_empty() {
        let r2 = (x, y + size * 1.45, bw, small * 1.5);
        ctx.draw_text(UI, sub, FONT, (r2.0 + 2.0, r2.1 + 2.0, r2.2, r2.3), 912, small, a, TextAlignXV1::Center,
                      TextAlignYV1::Center);
        ctx.draw_text(UI, sub, FONT, r2, 913, small, 0xf4_ee_dc_00 | a, TextAlignXV1::Center, TextAlignYV1::Center);
    }
}

/// 小提示：大字下面一条窄框。
fn toast(ctx: &mut StableClient<'_>, (w, h): (f32, f32), big_h: f32, line: &str, a: u32) {
    let size = (h * 0.028).max(17.0);
    let (bw, bh) = (w * 0.56, size * 1.7);
    let (x, y) = ((w - bw) / 2.0, h * 0.16 + big_h + 10.0);
    ctx.draw_rect(UI, x, y, bw, bh, 910, bh * 0.3, 0x14_12_10_00 | (a * 190 / 255));
    let r = (x, y, bw, bh);
    ctx.draw_text(UI, line, FONT, (r.0 + 2.0, r.1 + 2.0, r.2, r.3), 912, size, a, TextAlignXV1::Center,
                  TextAlignYV1::Center);
    ctx.draw_text(UI, line, FONT, r, 913, size, 0xf0_e6_c8_00 | a, TextAlignXV1::Center, TextAlignYV1::Center);
}

/// 一种计数的颜色（数字）。
pub fn badge_colour(kind: BadgeKind) -> u32 {
    match kind {
        BadgeKind::Arrests => 0x8c_c8_ff_00,
        BadgeKind::Escapes => 0xff_8c_dc_00,
        BadgeKind::Souls => 0x6c_ff_c8_00,
        BadgeKind::Freed => 0xff_f0_a0_00,
        BadgeKind::Crown => 0xc8_f4_ff_00,
    }
}

/// 冰冠冕：头像上缘的底座和三个尖（(x, y, w, h) 的方块，最后三个是尖上的亮点）。尖最高伸出头像上缘 2/10 个头像宽
/// （30 像素的头像 6 像素：行与行之间正好 6 像素，碰不到上一行）。
pub fn crown_parts(icon: (f32, f32, f32, f32)) -> [(f32, f32, f32, f32); 7] {
    let (x, y, w, _) = icon;
    let u = w / 10.0;
    let cx = x + w / 2.0;
    [
        (cx - 3.5 * u, y + 1.4 * u, 7.0 * u, 1.2 * u),
        (cx - 3.5 * u, y - 1.2 * u, 1.2 * u, 2.6 * u),
        (cx - 0.6 * u, y - 2.0 * u, 1.2 * u, 3.4 * u),
        (cx + 2.3 * u, y - 1.2 * u, 1.2 * u, 2.6 * u),
        (cx - 3.5 * u, y - 1.2 * u, 1.2 * u, 0.8 * u),
        (cx - 0.6 * u, y - 2.0 * u, 1.2 * u, 0.8 * u),
        (cx + 2.3 * u, y - 1.2 * u, 1.2 * u, 0.8 * u),
    ]
}

const KINDS: [BadgeKind; 5] = [BadgeKind::Arrests, BadgeKind::Escapes, BadgeKind::Souls, BadgeKind::Freed, BadgeKind::Crown];

/// 玩家栏头像上的计数和冠冕。
fn badges(ctx: &mut StableClient<'_>, t: usize, view: Option<(u64, u64)>) {
    let Some((m, s)) = view else { return };
    let all: Vec<Badge> = match BADGES.lock() {
        Ok(b) if !b.is_empty() => b.clone(),
        _ => return,
    };
    for panel in PANELS {
        if !shown(ctx, panel) {
            continue;
        }
        for (lane, row) in ctx.ui_child_names(panel).iter().enumerate() {
            for (side, team) in SIDES {
                let here: Vec<(BadgeKind, usize)> = KINDS
                    .iter()
                    .filter_map(|&k| badge_at(&all, view, team, lane, k, t).map(|v| (k, v)))
                    .collect();
                if here.is_empty() {
                    continue;
                }
                let Some(r) = ctx.ui_node_rect(&format!("{panel}.{row}.{side}.champion")).filter(|r| r.2 > 1.0 && r.3 > 1.0)
                else {
                    continue;
                };
                for (kind, value) in here {
                    if let Ok(mut d) = BADGED.lock() {
                        let key = (m, s, team, lane, kind, value);
                        if !d.contains(&key) {
                            d.push(key);
                            if d.len() > 512 {
                                d.drain(..256);
                            }
                            if let Some(k) = super::counted("badge") {
                                super::wlog(format!("BADGE m={m} s={s} screen t={t}: {kind:?} {value} on team {team} lane {lane} \
                                                     ({panel}.{row}.{side} at {:.0},{:.0} {:.0}x{:.0}) #{k}", r.0, r.1, r.2, r.3));
                            }
                        }
                    }
                    if kind == BadgeKind::Crown {
                        let parts = crown_parts(r);
                        for (i, p) in parts.iter().enumerate() {
                            let c = if i >= 4 { 0xff_ff_ff_ff } else { 0x9c_e6_ff_f0 };
                            ctx.draw_rect(UI, p.0 - 1.0, p.1 - 1.0, p.2 + 2.0, p.3 + 2.0, 906, 0.0, 0x1c_3c_64_d0);
                            ctx.draw_rect(UI, p.0, p.1, p.2, p.3, 907, 0.0, c);
                        }
                        continue;
                    }
                    let (bw, bh) = (r.2 * 0.62, r.3 * 0.52);
                    let (bx, by) = (r.0 + r.2 - bw * 0.85, r.1 + r.3 - bh * 0.8);
                    ctx.draw_rect(UI, bx, by, bw, bh, 906, bh * 0.35, 0x0c_0c_14_e0);
                    ctx.draw_text(UI, &value.to_string(), FONT, (bx, by, bw, bh), 907, bh * 0.95, badge_colour(kind) | 0xff,
                                  TextAlignXV1::Center, TextAlignYV1::Center);
                }
            }
        }
    }
}

/// 单独装的 league_eggs.dll 的客户端扩展：喂屏幕时钟（league_akshan 的 Overlay）、画公告和计数。
pub struct Overlay;

impl StableExtension for Overlay {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        if !ctx.is_in_game() {
            game_places::clock::observe(false, None);
            return;
        }
        let path = game_places::clock::CLOCK_PATH;
        let parts: Vec<&str> = path.split('.').collect();
        let shown = (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true));
        let text = shown.then(|| ctx.ui_text(path)).flatten();
        game_places::clock::observe(true, text.as_deref());
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        draw(ctx);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn n(m: u64, tick: usize, what: What) -> Note {
        Note { m, s: 1, tick, what }
    }

    fn caught(k: usize) -> What {
        What::Caught { cop: "league_caitlyn".into(), n: k }
    }

    fn start() -> What {
        What::CopsStart { cops: vec!["league_caitlyn".into()], robbers: vec!["league_jinx".into()] }
    }

    #[test]
    fn notes_queue_one_after_another() {
        let (a, b, c) = (n(7, 100, caught(1)), n(7, 120, caught(2)), n(7, 1000, caught(3)));
        let s = schedule(&[&b, &a, &c], SMALL_T);
        assert_eq!(s.iter().map(|x| x.0).collect::<Vec<_>>(), vec![100, 100 + SMALL_T, 1000]);
        assert_eq!(s[1].1, &b);
    }

    #[test]
    fn big_and_small_notes_keep_their_own_lanes() {
        let all = vec![n(7, 100, start()), n(7, 100, caught(1)), n(8, 100, caught(9))];
        let big = showing(&all, Some((7, 1)), true, 150).expect("the big one");
        assert_eq!((big.1.what.big(), big.2), (true, 50));
        let small = showing(&all, Some((7, 1)), false, 150).expect("the toast");
        assert_eq!(small.1.what, caught(1));
        // another match on screen: none of these
        assert!(showing(&all, Some((9, 1)), false, 150).is_none());
        assert!(showing(&all, None, true, 150).is_none());
        assert!(showing(&all, Some((7, 1)), true, 100 + BIG_T).is_none());
        assert!(showing(&all, Some((7, 1)), true, 99).is_none());
    }

    #[test]
    fn a_badge_shows_its_last_value_up_to_the_screen_tick() {
        let b = |tick, value| Badge { m: 7, s: 1, tick, team: 1, lane: 3, kind: BadgeKind::Arrests, value };
        let all = vec![b(100, 1), b(500, 2)];
        assert_eq!(badge_at(&all, Some((7, 1)), 1, 3, BadgeKind::Arrests, 99), None);
        assert_eq!(badge_at(&all, Some((7, 1)), 1, 3, BadgeKind::Arrests, 100), Some(1));
        assert_eq!(badge_at(&all, Some((7, 1)), 1, 3, BadgeKind::Arrests, 600), Some(2));
        assert_eq!(badge_at(&all, Some((7, 1)), 0, 3, BadgeKind::Arrests, 600), None);
        assert_eq!(badge_at(&all, Some((7, 1)), 1, 3, BadgeKind::Escapes, 600), None);
        assert_eq!(badge_at(&all, Some((8, 1)), 1, 3, BadgeKind::Arrests, 600), None);
    }

    #[test]
    fn it_fades_in_and_out() {
        assert!(alpha(0, BIG_T) < 60);
        assert_eq!(alpha(20, BIG_T), 255);
        assert_eq!(alpha(BIG_T - FADE_T, BIG_T), 255);
        assert!(alpha(BIG_T - 1, BIG_T) < 10);
        assert_eq!(alpha(BIG_T, BIG_T), 0);
    }

    #[test]
    fn the_words_follow_the_language() {
        let name = |id: &str| match id {
            "league_rengar" => "雷恩加尔".to_string(),
            "league_khazix" => "卡兹克".to_string(),
            x => x.to_string(),
        };
        let what = What::HuntStart { rengar: "league_rengar".into(), khazix: "league_khazix".into() };
        let (t, s) = words(Lang::Hans, &what, &name);
        assert_eq!(t, "狩猎开始！");
        assert!(s.contains("雷恩加尔 与 卡兹克"));
        assert_eq!(words(Lang::En, &what, &name).0, "The Hunt Is On!");
        let (t, s) = words(Lang::Hans, &caught(3), &name);
        assert_eq!((t.as_str(), s.as_str()), ("league_caitlyn 抓捕的罪犯：3（+1 金币）", ""));
        assert_eq!(lang_of("去而复还"), Lang::Hans);
        assert_eq!(lang_of("復仇迴力鏢"), Lang::Hant);
        assert_eq!(lang_of("Avengerang"), Lang::En);
        assert_eq!(lang_of("복수의 부메랑"), Lang::En);
        let q = What::QueensStart { queens: vec!["league_ashe".into(), "league_sejuani".into()] };
        assert!(words(Lang::Hans, &q, &name).1.starts_with("league_ashe、league_sejuani："));
    }

    #[test]
    fn every_note_has_a_title_in_every_language() {
        let s = || "x".to_string();
        let all = [
            What::HuntStart { rengar: s(), khazix: s() },
            What::HuntWon { winner: s(), loser: s() },
            What::QueensStart { queens: vec![s()] },
            What::Queen { queen: s() },
            start(),
            caught(1),
            What::Escaped { robber: s(), n: 1 },
            What::FishStart { thresh: vec![s()], others: vec![s()] },
            What::SoulTaken { thresh: s(), senna: s(), n: 1 },
            What::SoulsFreed { by: s(), thresh: s(), n: 1 },
            What::BearsStart { zilean: s(), volibear: s() },
            What::BearBounty { killer: s(), victim: s() },
            What::ZombieBounty { killer: s(), victim: s() },
            What::Plants { zyra: s(), maokai: s() },
            What::Ninjas { ninjas: vec![s()], hp: -1 },
            What::Charm { nidalee: s(), allies: vec![s()] },
            What::HuntSighted { seer: s(), seen: s() },
            What::Trophy { rengar: s(), khazix: s(), pct: 15 },
            What::Evolved { khazix: s(), rengar: s(), pct: 10 },
            What::Shades { wearer: s(), leona: s() },
            What::Sunlit { leona: s(), zyra: s() },
            What::Swallowed { fizz: s(), yordle: s() },
            What::Barefoot { cassiopeia: s() },
            What::DuoStart { xayah: s(), rakan: s() },
            What::DuoW { rakan: s(), xayah: s() },
            What::DuoE { rakan: s(), xayah: s() },
        ];
        for w in &all {
            for lang in [Lang::Hans, Lang::Hant, Lang::En] {
                let (t, sub) = words(lang, w, &|x| x.to_string());
                assert!(!t.is_empty() && !t.contains('|') && !sub.contains('|'), "{w:?} {lang:?}");
                // big notes carry a second line, toasts none
                assert_eq!(!sub.is_empty(), w.big(), "{w:?} {lang:?}");
            }
        }
    }

    /// 0.2.0's toasts with the game's names (the champion text of the main pack, zh-hans / zh-hant / en).
    #[test]
    fn the_new_toasts_read_with_the_names() {
        let hans = |id: &str| {
            match id {
                "league_rengar" => "雷恩加尔",
                "league_khazix" => "卡兹克",
                "league_vayne" => "薇恩",
                "league_leesin" => "李青",
                "league_ziggs" => "吉格斯",
                "league_leona" => "蕾欧娜",
                "league_zyra" => "婕拉",
                "league_fizz" => "菲兹",
                "league_tristana" => "崔丝塔娜",
                "league_cassiopeia" => "卡西奥佩娅",
                "league_xayah" => "霞",
                "league_rakan" => "洛",
                x => x,
            }
            .to_string()
        };
        let t = |w: What| words(Lang::Hans, &w, &hans).0;
        let id = |x: &str| x.to_string();
        assert_eq!(t(What::HuntSighted { seer: id("league_rengar"), seen: id("league_khazix") }),
                   "雷恩加尔 发现了 卡兹克！宿敌相见，分外眼红");
        assert_eq!(t(What::Trophy { rengar: id("league_rengar"), khazix: id("league_khazix"), pct: 15 }),
                   "狩猎战利品：雷恩加尔 拿下了 卡兹克 的头，攻击力 +15%");
        assert_eq!(t(What::Evolved { khazix: id("league_khazix"), rengar: id("league_rengar"), pct: 10 }),
                   "额外进化：卡兹克 猎杀了 雷恩加尔，攻击力 +10%");
        assert_eq!(t(What::Shades { wearer: id("league_vayne"), leona: id("league_leona") }),
                   "太阳镜防晒：薇恩 戴着墨镜，蕾欧娜 的烈阳每层少烧 1%");
        // what each wearer has on his eyes
        assert!(t(What::Shades { wearer: id("league_leesin"), leona: id("league_leona") }).contains("李青 戴着蒙眼布"));
        assert!(t(What::Shades { wearer: id("league_ziggs"), leona: id("league_leona") }).contains("吉格斯 戴着护目镜"));
        assert_eq!(eyewear("league_twitch").2, "eyepieces");
        assert_eq!(t(What::Sunlit { leona: id("league_leona"), zyra: id("league_zyra") }),
                   "光合作用：蕾欧娜 的阳光照在 婕拉 的植物上，植物长大了一号");
        assert_eq!(t(What::Swallowed { fizz: id("league_fizz"), yordle: id("league_tristana") }),
                   "鲨鱼吃小矮子：菲兹 的鲨鱼把 崔丝塔娜 一口吞了");
        assert_eq!(t(What::Barefoot { cassiopeia: id("league_cassiopeia") }),
                   "蛇女不需要鞋：卡西奥佩娅 没有脚，不穿鞋，每升一级移速多涨一点");
        assert_eq!(t(What::DuoStart { xayah: id("league_xayah"), rakan: id("league_rakan") }),
                   "霞洛联动：霞 和 洛 同队，她的羽衣分他一份，他的舞步飞得更远");
        assert_eq!(t(What::DuoW { rakan: id("league_rakan"), xayah: id("league_xayah") }),
                   "霞洛联动：洛 分到了 霞 的「致死羽衣」，攻速、移速提高");
        assert_eq!(t(What::DuoE { rakan: id("league_rakan"), xayah: id("league_xayah") }),
                   "霞洛联动：洛 的「轻舞成双」飞到 霞 身边，给她一层护盾");
        // the other two languages
        let en = |w: What| words(Lang::En, &w, &|x: &str| x.trim_start_matches("league_").to_string()).0;
        assert_eq!(en(What::Swallowed { fizz: id("league_fizz"), yordle: id("league_lulu") }),
                   "Shark Snack: fizz's shark swallowed lulu whole");
        let hant = words(Lang::Hant, &What::Barefoot { cassiopeia: id("league_cassiopeia") }, &|_: &str| "卡莎碧雅".to_string());
        assert_eq!(hant.0, "蛇女不需要鞋：卡莎碧雅 沒有腳，不穿鞋，每升一級移速多漲一點");
        // all of them toasts, none a banner
        for w in [What::HuntSighted { seer: id("a"), seen: id("b") }, What::Barefoot { cassiopeia: id("c") },
                  What::DuoE { rakan: id("r"), xayah: id("x") }] {
            assert!(!w.big());
        }
    }

    /// The skill names in the duo's toasts are the game's own (the main pack's champion text).
    #[test]
    fn the_duo_toasts_name_the_game_s_skills() {
        let text = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../league/text/champion.i18n"))
            .expect("the main pack's champion text");
        for (lang, plumage, dance) in [(Lang::Hans, "致死羽衣", "轻舞成双"), (Lang::Hant, "奪命疾翼", "戰鬥舞踊"),
                                       (Lang::En, "Deadly Plumage", "Battle Dance")] {
            // Xayah's skill2 is the plumage; Rakan's skill2 is "Grand Entrance + Battle Dance" (his W and E in one)
            assert!(text.contains(&format!("\"skill2\": \"{plumage}\"")), "Xayah's W {lang:?}");
            assert!(text.contains(&format!("{dance}\"")), "Rakan's E {lang:?}");
            let w = |what: What| words(lang, &what, &|x: &str| x.to_string()).0;
            assert!(w(What::DuoW { rakan: "r".into(), xayah: "x".into() }).contains(plumage), "{lang:?}");
            assert!(w(What::DuoE { rakan: "r".into(), xayah: "x".into() }).contains(dance), "{lang:?}");
        }
    }

    #[test]
    fn the_crown_sits_on_the_icon_top() {
        let p = crown_parts((100.0, 200.0, 30.0, 30.0));
        assert!(p.iter().all(|r| r.0 >= 100.0 && r.0 + r.2 <= 130.0));
        // the middle spike is the tallest; its tip is above the icon's top, inside the 6-px gap to the row above
        assert!(p[2].3 > p[1].3 && p[5].1 < 200.0);
        assert!(p.iter().all(|r| r.1 >= 194.0 && r.1 + r.3 <= 215.0));
        // the spikes stand on the band
        assert!((p[1].1 + p[1].3 - p[0].1).abs() < 0.01);
    }
}
