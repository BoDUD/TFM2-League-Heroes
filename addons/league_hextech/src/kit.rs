//! 英雄的特性（AI 选海克斯打分用）：游戏数据里每个英雄的分类（近战 / 远程 / 法师 / 辅助 / 刺客 / 坦克）和标签（物理 / 法术 /
//! 治疗 / 护盾 / 控制 / 近战 / 远程 / 坦克…）。模拟里读不到这些，所以进程里留一张表，三处往里补（只补没有的，有的不改）：
//! 客户端扩展进了生涯读一次（`champion_names` + `champion_brief`——0.1.0 的日志：这样只读得到游戏自带的 60 个，联盟、云顶这些
//! mod 的英雄一个没有，42 份模拟全按分路猜），BP 钩子每次看见的英雄多了就补（`champion_briefs`，后台比赛的 BP 都在它们的模拟
//! 之前），BP 画面上读英雄格子时把格子里表上没有的补上（`champion_brief`）。每份模拟在排座位时把十个人的特性抄一份，之后整局只用
//! 这一份：同一小局的几份模拟一样。
//!
//! 表里没有的英雄（表还没填、别的 mod 后加的）按分路猜（[`from_lane`]）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::augments::Traits;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Kit {
    pub category: Option<ChampionCategoryV1>,
    pub tags: Vec<ChampionTagV1>,
}

static TABLE: LazyLock<Mutex<HashMap<String, Kit>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static FILLED: AtomicBool = AtomicBool::new(false);

pub fn filled() -> bool {
    FILLED.load(Ordering::Acquire)
}

/// 往表里补（没有的才放，有的不改）。-> 补进去几个
pub fn fill(list: Vec<(String, Kit)>) -> usize {
    let Ok(mut t) = TABLE.lock() else { return 0 };
    let mut n = 0;
    for (name, kit) in list {
        if kit.category.is_none() && kit.tags.is_empty() {
            continue;
        }
        if let std::collections::hash_map::Entry::Vacant(e) = t.entry(name) {
            e.insert(kit);
            n += 1;
        }
    }
    if !t.is_empty() {
        FILLED.store(true, Ordering::Release);
    }
    n
}

pub fn has(name: &str) -> bool {
    TABLE.lock().map(|t| t.contains_key(name)).unwrap_or(false)
}

pub fn get(name: &str) -> Option<Kit> {
    if !filled() {
        return None;
    }
    TABLE.lock().ok().and_then(|t| t.get(name).cloned())
}

pub fn count() -> usize {
    TABLE.lock().map(|t| t.len()).unwrap_or(0)
}

#[cfg(test)]
pub(crate) fn reset_for_test(list: Vec<(String, Kit)>) {
    let mut t = TABLE.lock().unwrap();
    t.clear();
    FILLED.store(false, Ordering::Release);
    if !list.is_empty() {
        t.extend(list);
        FILLED.store(true, Ordering::Release);
    }
}

/// 从客户端补：`names` 里表上没有的，问 `champion_brief`。-> 补进去几个
pub fn fill_from_client(ctx: &StableClient<'_>, names: Vec<String>) -> usize {
    let list: Vec<(String, Kit)> = names
        .into_iter()
        .filter(|n| !has(n))
        .filter_map(|n| ctx.champion_brief(&n).map(|b| (n, Kit { category: b.category, tags: b.tags })))
        .collect();
    fill(list)
}

/// BP 钩子上次看见几个英雄（多了才再读一遍）。
static DRAFT_SEEN: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

/// 从 BP 钩子补。-> 补进去几个
pub fn fill_from_draft(ctx: &StableDraftContext<'_>) -> usize {
    let len = ctx.champion_briefs().len();
    if len <= DRAFT_SEEN.load(Ordering::Relaxed) {
        return 0;
    }
    DRAFT_SEEN.store(len, Ordering::Relaxed);
    let list: Vec<(String, Kit)> = (0..len)
        .filter_map(|id| {
            let name = ctx.champion_name(id)?.to_string();
            Some((name, Kit { category: ctx.champion_category(id), tags: ctx.champion_tags(id) }))
        })
        .collect();
    fill(list)
}

/// 只为填表挂的 BP 钩子：从来不改 BP（全是 Pass）。
pub struct Watch;

impl StableDraftHook for Watch {
    fn id(&self) -> String {
        "league_hextech_kit".into()
    }

    fn score_ban(&self, ctx: &StableDraftContext<'_>, _candidate: usize, _base: f32) -> StableDraftDecision {
        note_draft(ctx);
        StableDraftDecision::Pass
    }

    fn score_pick(&self, ctx: &StableDraftContext<'_>, _candidate: usize, _base: f32) -> StableDraftDecision {
        note_draft(ctx);
        StableDraftDecision::Pass
    }
}

fn note_draft(ctx: &StableDraftContext<'_>) {
    let n = fill_from_draft(ctx);
    if n > 0 {
        super::wlog(format!("KIT {n} more champions' classes and tags from the pick screen's hook ({} in all)", count()));
    }
}

/// 一个英雄的特性：表里有就按分类和标签算，没有就按分路猜。-> (特性, 是不是按表算的)
pub fn traits(kit: Option<&Kit>, lane: Option<LaneV1>) -> (Traits, bool) {
    match kit {
        Some(k) if k.category.is_some() || !k.tags.is_empty() => (from_kit(k, lane), true),
        _ => (from_lane(lane), false),
    }
}

pub fn from_kit(k: &Kit, lane: Option<LaneV1>) -> Traits {
    use ChampionCategoryV1 as C;
    use ChampionTagV1 as G;
    let has = |t: G| k.tags.contains(&t);
    let cat = k.category;
    let mut ad: f32 = if has(G::Ad) { 1.0 } else { 0.0 };
    let mut ap: f32 = if has(G::Ap) || has(G::Magic) { 1.0 } else { 0.0 };
    if ad > 0.0 && ap > 0.0 {
        (ad, ap) = (0.7, 0.7);
    }
    if ad == 0.0 && ap == 0.0 {
        if matches!(cat, Some(C::Magician | C::Util)) {
            ap = 1.0;
        } else {
            ad = 1.0;
        }
    }
    // (靠普攻, 靠技能, 坦克, 战士, 刺客, 辅助)
    let (attacker, caster, mut tank, bruiser, assassin, mut support): (f32, f32, f32, f32, f32, f32) = match cat {
        Some(C::Range) => (1.0, 0.2, 0.0, 0.0, 0.1, 0.0),
        Some(C::Melee) => (0.6, 0.3, 0.3, 1.0, 0.2, 0.0),
        Some(C::Magician) => (0.1, 1.0, 0.0, 0.0, 0.2, 0.1),
        Some(C::Util) => (0.1, 0.7, 0.1, 0.0, 0.0, 1.0),
        Some(C::Assassin) => (0.4, 0.5, 0.0, 0.2, 1.0, 0.0),
        Some(C::Tank) => (0.2, 0.3, 1.0, 0.4, 0.0, 0.2),
        None => (0.4, 0.4, 0.2, 0.3, 0.2, 0.1),
    };
    if cat == Some(C::Tank) {
        // 坦克也挂着法术标签（蕾欧娜、墨菲特）：伤害不是它的事
        ad *= 0.4;
        ap *= 0.4;
    }
    if has(G::Tank) {
        tank = f32::max(tank, 0.6);
    }
    if lane == Some(LaneV1::Support) {
        support += 0.5;
    }
    if has(G::Heal) || has(G::Shield) {
        support += 0.3;
    }
    let melee = if has(G::Melee) {
        1.0
    } else if has(G::Range) {
        0.0
    } else if matches!(cat, Some(C::Melee | C::Assassin | C::Tank)) {
        1.0
    } else {
        0.0
    };
    // 带不带控制：有标签的按标签（游戏的 CC 标签，金克丝也有）；只知道分类的按分类猜
    let cc = if has(G::Cc) {
        1.0
    } else if !k.tags.is_empty() {
        0.0
    } else {
        match cat {
            Some(C::Tank) => 0.6,
            Some(C::Util) => 0.5,
            Some(C::Magician) => 0.3,
            _ => 0.1,
        }
    };
    Traits { ad, ap, attacker, caster, tank, bruiser, assassin, support: support.min(1.0), melee, ranged: 1.0 - melee, cc }
}

/// 表里没有：按分路猜（上单战士、打野战士带点刺客、中单法师、下路射手、辅助）。
pub fn from_lane(lane: Option<LaneV1>) -> Traits {
    let t = |ad: f32, ap: f32, attacker: f32, caster: f32, tank: f32, bruiser: f32, assassin: f32, support: f32,
             melee: f32, cc: f32| Traits { ad, ap, attacker, caster, tank, bruiser, assassin, support, melee,
                                           ranged: 1.0 - melee, cc };
    match lane {
        Some(LaneV1::Top) => t(1.0, 0.0, 0.6, 0.3, 0.4, 1.0, 0.1, 0.0, 1.0, 0.4),
        Some(LaneV1::Jungle) => t(1.0, 0.0, 0.5, 0.3, 0.3, 0.7, 0.5, 0.0, 1.0, 0.5),
        Some(LaneV1::Mid) => t(0.0, 1.0, 0.1, 1.0, 0.0, 0.0, 0.3, 0.1, 0.0, 0.4),
        Some(LaneV1::Bottom) => t(1.0, 0.0, 1.0, 0.2, 0.0, 0.0, 0.1, 0.0, 0.0, 0.2),
        Some(LaneV1::Support) => t(0.0, 0.7, 0.1, 0.7, 0.3, 0.0, 0.0, 1.0, 0.3, 0.7),
        _ => t(0.5, 0.5, 0.4, 0.4, 0.2, 0.3, 0.2, 0.1, 0.5, 0.4),
    }
}

/// 日志里的一小段：`ad1.0 atk1.0 rng1.0`（只写不是 0 的）。
pub fn short(t: &Traits) -> String {
    let names = ["ad", "ap", "atk", "cast", "tank", "brs", "asn", "sup", "mel", "rng", "cc"];
    let parts: Vec<String> =
        names.iter().zip(t.arr()).filter(|(_, v)| *v != 0.0).map(|(n, v)| format!("{n}{v:.1}")).collect();
    if parts.is_empty() {
        "-".into()
    } else {
        parts.join(" ")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ChampionCategoryV1 as C;
    use ChampionTagV1 as G;

    fn kit(cat: C, tags: &[G]) -> Kit {
        Kit { category: Some(cat), tags: tags.to_vec() }
    }

    #[test]
    fn kits_read_like_their_class() {
        // Jinx: Range, AD Range CC
        let jinx = from_kit(&kit(C::Range, &[G::Ad, G::Range, G::Cc]), Some(LaneV1::Bottom));
        assert_eq!((jinx.ad, jinx.ap, jinx.attacker, jinx.ranged, jinx.melee, jinx.cc), (1.0, 0.0, 1.0, 1.0, 0.0, 1.0));
        // tags without CC: no CC; a class alone: a guess by class
        assert_eq!(from_kit(&kit(C::Range, &[G::Ad, G::Range]), None).cc, 0.0);
        assert_eq!(from_kit(&kit(C::Tank, &[]), None).cc, 0.6);
        // Leona: Tank, AP Magic Melee Tank CC, in the support lane - a tank first, a little support, not a mage
        let leona = from_kit(&kit(C::Tank, &[G::Ap, G::Magic, G::Melee, G::Tank, G::Cc]), Some(LaneV1::Support));
        assert_eq!(leona.tank, 1.0);
        assert!(leona.ap < 0.5 && leona.support >= 0.7 && leona.melee == 1.0, "{leona:?}");
        // Lulu: Util, AP Magic Range CC Shield
        let lulu = from_kit(&kit(C::Util, &[G::Ap, G::Magic, G::Range, G::Cc, G::Shield]), Some(LaneV1::Support));
        assert_eq!(lulu.support, 1.0);
        assert!(lulu.ap == 1.0 && lulu.ranged == 1.0, "{lulu:?}");
        // a hybrid: both damage types at 0.7
        let hy = from_kit(&kit(C::Melee, &[G::Ad, G::Ap, G::Melee]), None);
        assert_eq!((hy.ad, hy.ap), (0.7, 0.7));
        // no damage tag: the class decides
        assert_eq!(from_kit(&kit(C::Magician, &[]), None).ap, 1.0);
        assert_eq!(from_kit(&kit(C::Assassin, &[]), None).ad, 1.0);
    }

    /// Three sources add to the table: only what it lacks, never changing an entry; a brief with neither class nor tags
    /// adds nothing (0.1.0 filled it once from the client's 60 champions and never again: every mod hero by lane).
    #[test]
    fn the_table_grows_from_every_source() {
        let _g = super::super::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        reset_for_test(Vec::new());
        assert!(!filled());
        let jinx = kit(C::Range, &[G::Ad]);
        assert_eq!(fill(vec![("ghost".into(), kit(C::Assassin, &[])), ("league_jinx".into(), jinx.clone())]), 2);
        assert!(filled());
        // again with Jinx changed and one more: only the new one goes in
        assert_eq!(fill(vec![("league_jinx".into(), kit(C::Tank, &[])), ("league_leona".into(), kit(C::Tank, &[G::Tank]))]), 1);
        assert_eq!(get("league_jinx"), Some(jinx));
        assert_eq!(fill(vec![("league_zed".into(), Kit::default())]), 0, "nothing known about it");
        assert!(has("league_leona") && !has("league_zed"));
        assert_eq!(count(), 3);
        reset_for_test(Vec::new());
    }

    #[test]
    fn a_hero_without_a_kit_is_guessed_by_lane() {
        let (t, by_kit) = traits(None, Some(LaneV1::Mid));
        assert!(!by_kit && t.ap == 1.0 && t.caster == 1.0);
        let (t, _) = traits(None, Some(LaneV1::Bottom));
        assert!(t.ad == 1.0 && t.attacker == 1.0 && t.ranged == 1.0);
        let (t, _) = traits(Some(&Kit::default()), Some(LaneV1::Top));
        assert!(t.bruiser == 1.0 && t.melee == 1.0);
        let (_, by_kit) = traits(Some(&kit(C::Range, &[G::Ad])), None);
        assert!(by_kit);
        assert_eq!(short(&Traits { ad: 1.0, ranged: 1.0, ..Traits::ZERO }), "ad1.0 rng1.0");
    }
}
