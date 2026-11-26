//! 玩家在 BP 阶段给自己队伍选的海克斯（第 2 步，用户 2026-11-26：「海克斯可以让玩家自己选 AI就自动选」，比赛中途实时选做不到
//! ——屏幕上那场开场就在后台算完了——用户选了「就在 BP 阶段选」）。
//!
//! 一次 BP 一份记录（[`Record`]）：这一局 4 次的档位（全场同一档，对面 AI 也用它）、两边选了哪些英雄、玩家的每个英雄 4 次各三张卡
//! （发的时候四次互不相同，所以怎么选都不会重复）、刷新过的、选了哪张、是不是玩家自己点的（没点的按 AI 推荐）。BP 界面
//! （[`super::bp`]）往里写；模拟排座位时按「这一局两边各 5 个英雄」来认（[`for_sim`]）：服务器的两份预演和屏幕上的几份都认到
//! 同一份，打出来一样。头一份认它的模拟一来，这份就锁了，BP 界面再点也不变。屏幕上那一份知道（比赛, 局），记下来，之后
//! 同一局的模拟（屏幕的第二遍、回放）先按它找；存档里也存一份（[`encode`] / [`decode`]，客户端写），重开游戏看回放照样是这几张。

use std::sync::Mutex;

use super::augments::{by_key, Tier, Traits, AUGS};
use super::rules::{self, Rng, SCREENS};

/// 玩家的一次选择（一个英雄的第几次）。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Choice {
    /// 现在的三张、最先发的三张（刷新过的那几张不一样）
    pub cards: [u16; 3],
    pub first: [u16; 3],
    /// 拿了哪张（海克斯编号）
    pub chosen: u16,
    /// 是玩家自己点的（不是就是 AI 推荐的）
    pub by_user: bool,
    /// 技能海克斯放在哪个技能上（0.5.0：1 技能、2 技能 2、3 大招；0 = 没选，用 AI 默认的 [`crate::augments::ai_slot`]）
    pub slot: u8,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Mine {
    pub hero: String,
    pub picks: Vec<Choice>,
    /// 玩家按了「确定」：这 4 张都算玩家选的（AI 推荐的也是他认下的）
    pub confirmed: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Record {
    pub id: u64,
    /// 玩家是哪边（0 蓝、1 红）
    pub side: usize,
    pub tiers: [Tier; SCREENS],
    /// 两边选了的英雄，按选的先后
    pub blue: Vec<String>,
    pub red: Vec<String>,
    /// 玩家这边每个英雄的 4 次
    pub mine: Vec<Mine>,
    /// 发牌、刷新用的随机数（这份记录自己的）
    pub rng: u64,
    /// 屏幕上那一场认它的时候记下的（比赛, 局）
    pub bound: Option<(u64, u64)>,
    /// 有模拟用过了：锁了
    pub used: bool,
}

impl Record {
    pub fn new(id: u64, side: usize, seed: u64, weights: [u32; 3]) -> Record {
        Record { id, side: side.min(1), tiers: rules::tiers(seed, weights), blue: Vec::new(), red: Vec::new(), mine: Vec::new(),
                 rng: rules::splitmix(seed ^ 0x6270_7069_636b_0003), bound: None, used: false }
    }

    pub fn mine_of(&self, hero: &str) -> Option<&Mine> {
        self.mine.iter().find(|m| m.hero == hero)
    }

    fn rng(&mut self) -> Rng {
        self.rng = rules::splitmix(self.rng);
        Rng::new(self.rng)
    }

    /// 两边选到哪了：玩家这边新选的英雄发 4 次的牌（AI 推荐的先选上）；被换掉的（不在玩家这边了）去掉。锁了以后不变。
    pub fn set_lineup(&mut self, blue: Vec<String>, red: Vec<String>, traits: impl Fn(&str) -> Traits) {
        if self.used {
            return;
        }
        let ours = if self.side == 0 { blue.clone() } else { red.clone() };
        self.blue = blue;
        self.red = red;
        self.mine.retain(|m| ours.contains(&m.hero));
        for hero in ours {
            if self.mine_of(&hero).is_some() {
                continue;
            }
            let t = traits(&hero);
            let mut rng = self.rng();
            let mut used: Vec<usize> = Vec::new();
            let mut picks = Vec::with_capacity(SCREENS);
            for k in 0..SCREENS {
                let cards = rules::deal(&mut rng, self.tiers[k], &used).unwrap_or([0, 1, 2]);
                used.extend(cards);
                let c = [cards[0] as u16, cards[1] as u16, cards[2] as u16];
                picks.push(Choice { cards: c, first: c, chosen: c[0], by_user: false, slot: 0 });
            }
            let mut m = Mine { hero, picks, confirmed: false };
            recommend(&mut m, &t, &mut rng, true);
            self.mine.push(m);
        }
    }

    /// 玩家点了第 `k` 次的第 `card` 张。-> 变了没有
    pub fn choose(&mut self, hero: &str, k: usize, card: usize) -> bool {
        if self.used || card >= 3 {
            return false;
        }
        let Some(m) = self.mine.iter_mut().find(|m| m.hero == hero) else { return false };
        let Some(c) = m.picks.get_mut(k) else { return false };
        if c.chosen != c.cards[card] {
            c.slot = 0;
        }
        c.chosen = c.cards[card];
        c.by_user = true;
        true
    }

    /// 玩家给第 `k` 次拿的技能海克斯选技能（1 技能、2 技能 2、3 大招；拿的不是技能海克斯、锁了：不改）。-> 改了没有
    pub fn set_slot(&mut self, hero: &str, k: usize, slot: u8) -> bool {
        if self.used || !(1..=3).contains(&slot) {
            return false;
        }
        let Some(m) = self.mine.iter_mut().find(|m| m.hero == hero) else { return false };
        let Some(c) = m.picks.get_mut(k) else { return false };
        if !crate::augments::skill_aug(AUGS[c.chosen as usize].ev) {
            return false;
        }
        c.slot = slot;
        c.by_user = true;
        true
    }

    /// 玩家刷新第 `k` 次的第 `card` 张（每张一次）：换一张同档的，这个英雄四次里都没出现过的；这一档抽空了就不刷新。
    /// 刷掉的正好是选着的那张：改成新的那张里 AI 推荐的（算玩家没点过）。-> 刷了没有
    pub fn reroll(&mut self, hero: &str, k: usize, card: usize, traits: &Traits) -> bool {
        if self.used || card >= 3 {
            return false;
        }
        let mut rng = self.rng();
        let Some(m) = self.mine.iter_mut().find(|m| m.hero == hero) else { return false };
        let Some(c) = m.picks.get(k) else { return false };
        if c.cards[card] != c.first[card] {
            return false;
        }
        let seen: Vec<usize> =
            m.picks.iter().flat_map(|p| p.cards.iter().chain(p.first.iter()).map(|&x| x as usize)).collect();
        let tier = AUGS[c.cards[card] as usize].tier;
        let Some(new) = rules::draw_card(&mut rng, tier, &seen, &[], false) else { return false };
        let was = c.cards[card];
        let c = &mut m.picks[k];
        c.cards[card] = new as u16;
        if c.chosen == was {
            c.by_user = false;
            let taken: Vec<usize> = m.picks.iter().take(k).map(|p| p.chosen as usize).collect();
            m.picks[k].chosen = best_card(&m.picks[k].cards, traits, &taken);
        }
        true
    }

    /// 第 `k` 次的第 `card` 张还能不能刷新：没刷过，这一档还有这个英雄四次里都没出现过的卡（海克斯只有 20 个，同一档出现两次
    /// 时常常抽空）。
    pub fn reroll_left(&self, hero: &str, k: usize, card: usize) -> bool {
        let Some(m) = self.mine_of(hero) else { return false };
        let Some(c) = m.picks.get(k) else { return false };
        if card >= 3 || c.cards[card] != c.first[card] {
            return false;
        }
        let seen: Vec<u16> = m.picks.iter().flat_map(|p| p.cards.iter().chain(p.first.iter()).copied()).collect();
        let tier = AUGS[c.cards[card] as usize].tier;
        super::augments::pool(tier).into_iter().any(|a| !seen.contains(&(a as u16)))
    }

    /// 这个英雄全部按 AI 推荐（玩家点过的、确定过的都改回去；只在现在的三张里重新挑，不再换卡；刷新过的卡不会变回来）。
    pub fn all_ai(&mut self, hero: &str, traits: &Traits) {
        if self.used {
            return;
        }
        let mut rng = self.rng();
        if let Some(m) = self.mine.iter_mut().find(|m| m.hero == hero) {
            for c in m.picks.iter_mut() {
                c.by_user = false;
            }
            m.confirmed = false;
            recommend(m, traits, &mut rng, false);
        }
    }

    /// 玩家按「确定」：认下这个英雄现在的 4 张。-> 变了没有
    pub fn confirm(&mut self, hero: &str) -> bool {
        if self.used {
            return false;
        }
        match self.mine.iter_mut().find(|m| m.hero == hero) {
            Some(m) if !m.confirmed => {
                m.confirmed = true;
                true
            }
            _ => false,
        }
    }

    /// 「全部确定」。-> 确定了几个
    pub fn confirm_all(&mut self) -> usize {
        if self.used {
            return 0;
        }
        let mut n = 0;
        for m in self.mine.iter_mut().filter(|m| !m.confirmed) {
            m.confirmed = true;
            n += 1;
        }
        n
    }

    /// 确定了几个英雄（BP 标题栏的「已选 x/5」）。
    pub fn confirmed(&self) -> usize {
        self.mine.iter().filter(|m| m.confirmed).count()
    }

    /// 下一个还没确定的英雄（在 `after` 后面找，绕回开头；都确定了：None）。
    pub fn next_open(&self, after: usize) -> Option<usize> {
        let n = self.mine.len();
        (1..=n).map(|d| (after + d) % n.max(1)).find(|&i| self.mine.get(i).is_some_and(|m| !m.confirmed))
    }

    /// 玩家这边有几个英雄是玩家定的（点过卡或按了确定）。
    pub fn touched(&self) -> usize {
        self.mine.iter().filter(|m| m.confirmed || m.picks.iter().any(|c| c.by_user)).count()
    }

    fn lineup_is(&self, blue: &[String], red: &[String]) -> bool {
        let same = |a: &[String], b: &[String]| {
            a.len() == b.len() && a.iter().all(|x| b.contains(x)) && b.iter().all(|x| a.contains(x))
        };
        same(&self.blue, blue) && same(&self.red, red)
    }
}

/// 没点过的那几次按 AI 推荐，和比赛里的 AI 一样拿三张里分最高的；前面拿了的算进搭配。
///
/// `replace`（发牌的时候）：先把比赛里的 AI 会刷新的（[`rules::reroll_bar`]、[`rules::worth_reroll`]）换掉（这一档还有这个英雄
/// 四次里没出现过的卡时），
/// 玩家 2026-11-26 的截图：塔莉垭（法师）6 级三张都不合适，不换就默认拿了「钝器 +20% 攻击力」。换掉的算在发牌里（`first` 也改成
/// 新的那张）：0.2.1 / 0.3.x 只改了 `cards`，面板上这张卡写着「已刷新」、玩家这张卡的那次刷新也被用掉了（用户：「有点bug吧 AI默认
/// 选择的直接显示已刷新」）。换下来的那张玩家从来没看见过，以后刷新再抽到它也没关系。「全部按 AI 推荐」不换卡，只在现在的三张里挑。
fn recommend(m: &mut Mine, t: &Traits, rng: &mut Rng, replace: bool) {
    let mut taken: Vec<usize> = Vec::new();
    for k in 0..m.picks.len() {
        if !m.picks[k].by_user {
            if replace {
                let tier = AUGS[m.picks[k].first[0] as usize].tier;
                let bar = rules::reroll_bar(t, &taken, 0.0, tier);
                let s = |x: u16| rules::score(x as usize, t, &taken, 0.0);
                let mut order = [0usize, 1, 2];
                order.sort_by(|&a, &b| s(m.picks[k].cards[a]).total_cmp(&s(m.picks[k].cards[b])));
                for j in order {
                    let c = &m.picks[k];
                    if c.cards[j] != c.first[j] {
                        continue;
                    }
                    let other = (0..3).filter(|&i| i != j).map(|i| s(c.cards[i])).fold(f32::MIN, f32::max);
                    let seen: Vec<usize> =
                        m.picks.iter().flat_map(|p| p.cards.iter().chain(p.first.iter()).map(|&x| x as usize)).collect();
                    let ctier = AUGS[c.cards[j] as usize].tier;
                    if !rules::worth_reroll(s(c.cards[j]), other, bar, &rules::left_scores(t, &taken, 0.0, ctier, &seen)) {
                        continue;
                    }
                    if let Some(new) = rules::draw_card(rng, ctier, &seen, &[], false) {
                        m.picks[k].cards[j] = new as u16;
                        m.picks[k].first[j] = new as u16;
                    }
                }
            }
            m.picks[k].chosen = best_card(&m.picks[k].cards, t, &taken);
        }
        taken.push(m.picks[k].chosen as usize);
    }
}

pub fn best_card(cards: &[u16; 3], t: &Traits, taken: &[usize]) -> u16 {
    let mut best = cards[0];
    let mut best_s = f32::MIN;
    for &c in cards {
        let s = rules::score(c as usize, t, taken, 0.0);
        if s > best_s {
            (best, best_s) = (c, s);
        }
    }
    best
}

// ===================== 进程里的记录 =====================

static RECORDS: Mutex<Vec<Record>> = Mutex::new(Vec::new());
/// 最多留几份（最早的先丢；锁了还没记下比赛的、记下了的都算）。
const MOST: usize = 24;

pub fn with<R>(f: impl FnOnce(&mut Vec<Record>) -> R) -> R {
    let mut l = RECORDS.lock().unwrap_or_else(|e| e.into_inner());
    f(&mut l)
}

/// 新的一次 BP：放进一份新的记录（同一边还没锁的旧记录丢掉——那次 BP 没打成）。-> 编号
pub fn open(rec: Record) -> u64 {
    let id = rec.id;
    with(|l| {
        l.retain(|r| r.used || r.bound.is_some());
        l.push(rec);
        if l.len() > MOST {
            let n = l.len() - MOST;
            l.drain(..n);
        }
    });
    id
}

pub fn get(id: u64) -> Option<Record> {
    with(|l| l.iter().find(|r| r.id == id).cloned())
}

pub fn edit<R>(id: u64, f: impl FnOnce(&mut Record) -> R) -> Option<R> {
    with(|l| l.iter_mut().find(|r| r.id == id).map(f))
}

/// 存档里读回来的（已经锁了、记着比赛）：同一局的不重复放。
pub fn restore(rec: Record) {
    with(|l| {
        if !l.iter().any(|r| r.bound.is_some() && r.bound == rec.bound) {
            l.push(rec);
        }
    });
}

/// 模拟排座位时：这一局用哪份记录（没有：None，全员 AI）。`screen` 是屏幕上那几份模拟的（比赛, 局）；`m` 是比赛（预演
/// 只知道比赛，不知道第几局）。先按（比赛, 局）找记下的；再找最新的、两边英雄都对得上的、没记到别的局上的。找到就锁上，
/// 屏幕上的那一份顺便记下（比赛, 局）。
pub fn for_sim(blue: &[String], red: &[String], m: Option<u64>, screen: Option<(u64, u64)>) -> Option<Record> {
    with(|l| {
        if let Some(ms) = screen {
            if let Some(r) = l.iter().find(|r| r.bound == Some(ms) && r.lineup_is(blue, red)) {
                return Some(r.clone());
            }
        }
        let r = l.iter_mut().rev().find(|r| {
            r.lineup_is(blue, red)
                && r.bound.is_none_or(|(bm, _)| m.is_none_or(|mm| mm == bm) && screen.is_none_or(|ms| r.bound == Some(ms)))
        })?;
        r.used = true;
        if let (Some(ms), None) = (screen, r.bound) {
            r.bound = Some(ms);
            UNSAVED.lock().unwrap_or_else(|e| e.into_inner()).push(r.id);
        }
        Some(r.clone())
    })
}

/// 记下了（比赛, 局）、还没写进存档的记录（客户端写完拿掉）。
static UNSAVED: Mutex<Vec<u64>> = Mutex::new(Vec::new());

pub fn take_unsaved() -> Vec<Record> {
    let ids = std::mem::take(&mut *UNSAVED.lock().unwrap_or_else(|e| e.into_inner()));
    ids.into_iter().filter_map(get).collect()
}

pub fn unsave_again(ids: &[u64]) {
    UNSAVED.lock().unwrap_or_else(|e| e.into_inner()).extend_from_slice(ids);
}

#[cfg(test)]
pub(crate) fn clear() {
    with(|l| l.clear());
    UNSAVED.lock().unwrap().clear();
}

// ===================== 存档里的样子 =====================

/// 存档里的键：`league_hextech:pick:<比赛>:<局>`。
pub const SAVE_PREFIX: &str = "league_hextech:pick:";

pub fn save_key(m: u64, s: u64) -> String {
    format!("{SAVE_PREFIX}{m}:{s}")
}

/// 一行字：`1|边|档位4个|蓝的英雄,..|红的英雄,..|英雄=卡,卡,卡/先前,先前,先前/拿的/u或a;...(四次)|...`，海克斯按 key 存
/// （以后加了新的、换了顺序也读得回来）。
pub fn encode(r: &Record) -> String {
    let k = |i: u16| AUGS[i as usize].key;
    let tiers: String = r.tiers.iter().map(|t| char::from(b'0' + t.code())).collect();
    let mine: Vec<String> = r
        .mine
        .iter()
        .map(|m| {
            let picks: Vec<String> = m
                .picks
                .iter()
                .map(|c| {
                    let slot = if c.slot > 0 { format!("/{}", c.slot) } else { String::new() };
                    format!("{},{},{}/{},{},{}/{}/{}{slot}", k(c.cards[0]), k(c.cards[1]), k(c.cards[2]), k(c.first[0]),
                            k(c.first[1]), k(c.first[2]), k(c.chosen), if c.by_user { "u" } else { "a" })
                })
                .collect();
            format!("{}{}={}", if m.confirmed { "!" } else { "" }, m.hero, picks.join(";"))
        })
        .collect();
    format!("1|{}|{tiers}|{}|{}|{}", r.side, r.blue.join(","), r.red.join(","), mine.join("|"))
}

/// [`encode`] 反过来（读不懂、有不认识的海克斯：None）。读回来的算锁了、记着 (m, s)。
pub fn decode(text: &str, m: u64, s: u64, id: u64) -> Option<Record> {
    let mut parts = text.split('|');
    if parts.next()? != "1" {
        return None;
    }
    let side: usize = parts.next()?.parse().ok()?;
    let tiers_s = parts.next()?;
    let mut tiers = [Tier::Gold; SCREENS];
    if tiers_s.len() != SCREENS {
        return None;
    }
    for (i, ch) in tiers_s.bytes().enumerate() {
        tiers[i] = Tier::from_code(ch.checked_sub(b'0')?)?;
    }
    let list = |s: &str| -> Vec<String> { s.split(',').filter(|x| !x.is_empty()).map(str::to_string).collect() };
    let blue = list(parts.next()?);
    let red = list(parts.next()?);
    let aug = |s: &str| by_key(s).map(|i| i as u16);
    let three = |s: &str| -> Option<[u16; 3]> {
        let v: Vec<u16> = s.split(',').map(aug).collect::<Option<Vec<u16>>>()?;
        (v.len() == 3).then(|| [v[0], v[1], v[2]])
    };
    let mut mine = Vec::new();
    for part in parts.filter(|p| !p.is_empty()) {
        let (hero, rest) = part.split_once('=')?;
        let mut picks = Vec::new();
        for p in rest.split(';') {
            let f: Vec<&str> = p.split('/').collect();
            // 0.5.0 起技能海克斯多一段：选的技能
            if f.len() != 4 && f.len() != 5 {
                return None;
            }
            let slot = match f.get(4) {
                Some(x) => x.parse::<u8>().ok().filter(|s| (1..=3).contains(s))?,
                None => 0,
            };
            picks.push(Choice { cards: three(f[0])?, first: three(f[1])?, chosen: aug(f[2])?, by_user: f[3] == "u", slot });
        }
        if picks.len() != SCREENS {
            return None;
        }
        let (confirmed, hero) = match hero.strip_prefix('!') {
            Some(h) => (true, h),
            None => (false, hero),
        };
        mine.push(Mine { hero: hero.to_string(), picks, confirmed });
    }
    Some(Record { id, side: side.min(1), tiers, blue, red, mine, rng: 0, bound: Some((m, s)), used: true })
}

#[cfg(test)]
mod tests {
    use super::super::augments::by_key;
    use super::*;

    fn marksman() -> Traits {
        Traits { ad: 1.0, attacker: 1.0, ranged: 1.0, caster: 0.2, ..Traits::ZERO }
    }

    fn v(names: &[&str]) -> Vec<String> {
        names.iter().map(|s| s.to_string()).collect()
    }

    const BLUE: [&str; 5] = ["league_garen", "league_leesin", "league_ahri", "league_jinx", "league_leona"];
    const RED: [&str; 5] = ["league_darius", "league_elise", "league_syndra", "league_caitlyn", "league_lulu"];

    fn full(seed: u64) -> Record {
        let mut r = Record::new(seed, 0, seed, [35, 45, 20]);
        r.set_lineup(v(&BLUE), v(&RED), |_| marksman());
        r
    }

    /// 0.5.0：技能海克斯选的技能存进记录、存档读回来一样；换了卡回到 AI 默认；不是技能海克斯不让选。
    #[test]
    fn a_skill_augments_ability_is_kept() {
        let mut r = full(5);
        let hero = r.mine[0].hero.clone();
        let (siphon, deft, hearty) = (by_key("siphon").unwrap() as u16, by_key("deft").unwrap() as u16, by_key("hearty").unwrap() as u16);
        r.mine[0].picks[1].cards = [siphon, deft, hearty];
        r.mine[0].picks[1].first = [siphon, deft, hearty];
        assert!(r.choose(&hero, 1, 0));
        assert!(r.set_slot(&hero, 1, 3));
        assert!(!r.set_slot(&hero, 1, 4), "only 1-3");
        assert_eq!(r.mine[0].picks[1].slot, 3);
        r.bound = Some((3, 1));
        let back = decode(&encode(&r), 3, 1, r.id).unwrap();
        assert_eq!(back.mine, r.mine);
        // a record without the ability (0.4.0's) still reads
        let old = encode(&r).replace("/u/3", "/u");
        assert_eq!(decode(&old, 3, 1, r.id).unwrap().mine[0].picks[1].slot, 0);
        assert!(r.choose(&hero, 1, 1), "another card");
        assert_eq!(r.mine[0].picks[1].slot, 0, "back to the AI's");
        assert!(!r.set_slot(&hero, 1, 2), "deft takes no ability");
    }

    #[test]
    fn each_of_our_heroes_gets_four_screens_of_distinct_cards() {
        for seed in 0..500u64 {
            let r = full(seed);
            assert_eq!(r.mine.len(), 5);
            for m in &r.mine {
                assert_eq!(m.picks.len(), SCREENS);
                let mut all: Vec<u16> = m.picks.iter().flat_map(|c| c.cards).collect();
                let mut ever: Vec<u16> = m.picks.iter().flat_map(|c| c.cards.iter().chain(c.first.iter()).copied()).collect();
                for (k, c) in m.picks.iter().enumerate() {
                    assert!(c.cards.contains(&c.chosen) && !c.by_user);
                    // the deal (`first`, the AI default's swaps in it): the screen's tier, unless this hero's earlier screens
                    // took every card of it (then borrowed)
                    let in_tier = c.first.iter().filter(|&&x| AUGS[x as usize].tier == r.tiers[k]).count();
                    let earlier: Vec<u16> = m.picks[..k].iter().flat_map(|p| p.first).collect();
                    let left = super::super::augments::pool(r.tiers[k]).into_iter().filter(|&a| !earlier.contains(&(a as u16))).count();
                    assert!(in_tier == left.min(3), "seed {seed}: {c:?} for {:?} ({left} left)", r.tiers[k]);
                    // a reroll keeps the card's tier
                    for j in 0..3 {
                        assert_eq!(AUGS[c.cards[j] as usize].tier, AUGS[c.first[j] as usize].tier);
                    }
                }
                all.sort();
                all.dedup();
                assert_eq!(all.len(), 12, "seed {seed}: the four screens share a card");
                // and a rerolled card was never on this hero's table before

                ever.sort();
                ever.dedup();
                let rerolls = m.picks.iter().flat_map(|c| (0..3).filter(move |&j| c.cards[j] != c.first[j])).count();
                assert_eq!(ever.len(), 12 + rerolls, "seed {seed}");
                // so whatever is chosen, never one twice
            }
            assert!(!(r.tiers[0] == Tier::Silver && r.tiers[1] == Tier::Silver));
        }
    }

    #[test]
    fn the_ai_default_takes_what_fits_and_the_player_can_change_it() {
        let mut r = full(7);
        let jinx = "league_jinx";
        let m = r.mine_of(jinx).unwrap().clone();
        let mut taken = Vec::new();
        for c in &m.picks {
            assert_eq!(c.chosen, best_card(&c.cards, &marksman(), &taken), "the best of the three, with what came before");
            taken.push(c.chosen as usize);
        }
        // the player clicks the third card of the second screen
        assert!(r.choose(jinx, 1, 2));
        let c = &r.mine_of(jinx).unwrap().picks[1];
        assert_eq!((c.chosen, c.by_user), (c.cards[2], true));
        assert_eq!(r.touched(), 1);
        // back to the AI's choice
        r.all_ai(jinx, &marksman());
        assert!(r.mine_of(jinx).unwrap().picks.iter().all(|c| !c.by_user));
        assert_eq!(r.touched(), 0);
        assert!(!r.choose("league_darius", 0, 0), "not our hero");
        assert!(!r.choose(jinx, 9, 0) && !r.choose(jinx, 0, 3));
    }

    /// The player's screenshot (2026-11-26): Taliyah, a mage, offered three silver cards that do nothing for her, was
    /// left on +20% attack damage. The default swaps out what the AI would reroll first: a mage's defaults are magic
    /// ones nearly always. The swaps are part of the deal (0.3.2, the user: 「AI默认选择的直接显示已刷新」): no card shows
    /// as rerolled and every card keeps the player's reroll; "all to the AI" only picks again among the cards on the table.
    #[test]
    fn the_default_swaps_what_does_not_fit_and_leaves_the_rerolls() {
        let mage = Traits { ap: 1.0, caster: 1.0, ranged: 1.0, attacker: 0.1, assassin: 0.2, ..Traits::ZERO };
        let magic = super::super::rules::tests::MAGIC;
        let (mut hits, mut n, mut swapped, mut can) = (0, 0, 0, 0);
        for seed in 0..300u64 {
            let mut r = Record::new(seed, 0, seed, [35, 45, 20]);
            // the deal as it came, before the AI's swaps (set_lineup's first draws)
            let mut probe = Record::new(seed, 0, seed, [35, 45, 20]);
            let mut rng = probe.rng();
            let mut used: Vec<usize> = Vec::new();
            let mut dealt = Vec::new();
            for k in 0..SCREENS {
                let cards = rules::deal(&mut rng, probe.tiers[k], &used).unwrap();
                used.extend(cards);
                dealt.push(cards);
            }
            r.set_lineup(v(&["league_taliyah"]), vec![], |_| mage);
            let hero = "league_taliyah";
            for (k, c) in r.mine[0].picks.iter().enumerate() {
                n += 1;
                hits += magic.contains(&AUGS[c.chosen as usize].key) as usize;
                swapped += (0..3).filter(|&j| c.first[j] as usize != dealt[k][j]).count();
                assert_eq!(c.cards, c.first, "seed {seed}: nothing shows as rerolled");
                can += (0..3).filter(|&j| r.reroll_left(hero, k, j)).count();
            }
            // all to the AI: the same cards, the best of them
            let before: Vec<[u16; 3]> = r.mine[0].picks.iter().map(|c| c.cards).collect();
            r.all_ai(hero, &mage);
            let after: Vec<[u16; 3]> = r.mine[0].picks.iter().map(|c| c.cards).collect();
            assert_eq!(before, after, "seed {seed}: no card swapped by the button");
        }
        assert!(hits as f64 >= 0.85 * n as f64, "{hits} magic defaults of {n}");
        assert!(swapped > 0, "the AI swapped nothing");
        // every card can be rerolled once by the player (but where a tier ran dry for this hero)
        assert!(can as f64 >= 0.9 * (n * 3) as f64, "{can} of {} cards can be rerolled", n * 3);
    }

    #[test]
    fn confirm_counts_the_hero_and_moves_on() {
        let mut r = full(21);
        assert_eq!((r.confirmed(), r.next_open(0)), (0, Some(1)));
        assert!(r.confirm("league_garen"));
        assert!(!r.confirm("league_garen"), "once");
        assert_eq!(r.confirmed(), 1);
        assert_eq!(r.touched(), 1);
        assert_eq!(r.next_open(0), Some(1));
        assert_eq!(r.next_open(4), Some(1), "wraps round, skipping the confirmed");
        assert_eq!(r.confirm_all(), 4);
        assert_eq!((r.confirmed(), r.next_open(0)), (5, None));
        // back to the AI: not confirmed any more
        r.all_ai("league_ahri", &marksman());
        assert_eq!(r.confirmed(), 4);
        // locked: nothing changes
        r.used = true;
        assert!(!r.confirm("league_ahri") && r.confirm_all() == 0);
        // the save keeps it
        r.bound = Some((3, 1));
        let back = decode(&encode(&r), 3, 1, r.id).unwrap();
        assert_eq!(back.mine.iter().filter(|m| m.confirmed).count(), 4);
        assert_eq!(back.mine, r.mine);
    }

    /// Every card fits a little: the AI's default rerolls next to nothing, the player has the rerolls (with a misfit the
    /// default has already rerolled the bad cards: see the_default_rerolls_what_does_not_fit).
    fn neutral() -> Traits {
        Traits { ad: 0.5, ap: 0.5, attacker: 0.5, caster: 0.5, tank: 0.5, bruiser: 0.5, assassin: 0.5, support: 0.5,
                 melee: 0.5, ranged: 0.5, cc: 0.5 }
    }

    #[test]
    fn a_reroll_brings_an_unseen_card_of_the_same_tier_once() {
        let mut hits = 0;
        for seed in 0..300u64 {
            let mut r = Record::new(seed, 0, seed, [35, 45, 20]);
            r.set_lineup(v(&BLUE), v(&RED), |_| neutral());
            let hero = "league_ahri";
            let before = r.mine_of(hero).unwrap().clone();
            let k = (seed % 4) as usize;
            let card = (seed % 3) as usize;
            let left = r.reroll_left(hero, k, card);
            let done = r.reroll(hero, k, card, &marksman());
            assert_eq!(left, done, "seed {seed}: the panel shows a reroll exactly when one goes through");
            if done {
                hits += 1;
                let after = r.mine_of(hero).unwrap();
                let (old, new) = (before.picks[k].cards[card], after.picks[k].cards[card]);
                assert_ne!(old, new);
                assert_eq!(AUGS[old as usize].tier, AUGS[new as usize].tier);
                let seen: Vec<u16> = before.picks.iter().flat_map(|c| c.cards).collect();
                assert!(!seen.contains(&new), "seed {seed}: the new card was on the table already");
                assert_eq!(after.picks[k].first, before.picks[k].first, "the first deal is kept");
                assert!(after.picks[k].cards.contains(&after.picks[k].chosen));
                // only once a card
                assert!(!r.reroll(hero, k, card, &marksman()));
            }
        }
        // 20 augments: a tier seen twice on one hero's four screens often runs dry (gold 7, prismatic 5), and the AI's
        // default has rerolled the cards with a downside (Glass Cannon, Celestial Body) already
        assert!(hits > 100, "rerolls find a card often ({hits} of 300)");
    }

    #[test]
    fn a_lineup_change_deals_the_new_hero_and_drops_the_old() {
        let mut r = Record::new(1, 1, 99, [35, 45, 20]);
        r.set_lineup(vec![], v(&RED[..2]), |_| marksman());
        assert_eq!(r.mine.iter().map(|m| m.hero.as_str()).collect::<Vec<_>>(), &RED[..2]);
        let first = r.mine_of(RED[0]).unwrap().clone();
        r.set_lineup(v(&BLUE[..3]), v(&RED[..3]), |_| marksman());
        assert_eq!(r.mine.len(), 3);
        assert_eq!(r.mine_of(RED[0]).unwrap(), &first, "a hero's cards stay as dealt");
        // a swap took Lulu out (not ours any more): her cards go
        r.set_lineup(v(&BLUE), vec!["league_darius".into(), "league_elise".into(), "league_zed".into()], |_| marksman());
        assert!(r.mine_of(RED[2]).is_none() && r.mine_of("league_zed").is_some());
    }

    #[test]
    fn the_simulations_of_the_set_find_it_and_lock_it() {
        let _g = super::super::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        clear();
        let id = open(full(5));
        let (b, r) = (v(&BLUE), v(&RED));
        // a background match with other heroes: nothing
        assert!(for_sim(&v(&RED), &v(&BLUE), Some(1), None).is_none(), "sides swapped is not this set");
        assert!(for_sim(&v(&["league_zed"]), &r, Some(1), None).is_none());
        // the two presims (match 40, no set), then the screen's (match 40, set 2)
        let a = for_sim(&b, &r, Some(40), None).expect("presim");
        let c = for_sim(&b, &r, Some(40), None).expect("its twin");
        assert_eq!(a, c);
        assert!(get(id).unwrap().used, "locked once used");
        let view = for_sim(&b, &r, Some(40), Some((40, 2))).expect("the screen");
        assert_eq!(view.bound, Some((40, 2)));
        assert_eq!(take_unsaved().iter().map(|x| x.id).collect::<Vec<_>>(), vec![id]);
        assert!(take_unsaved().is_empty());
        // locked: the panel's clicks change nothing now
        assert_eq!(edit(id, |x| x.choose("league_jinx", 0, 2)), Some(false));
        // the next set with the very same ten heroes: a new BP's record, the old one still found by its set
        let id2 = open(full(6));
        assert_eq!(for_sim(&b, &r, Some(40), None).map(|x| x.id), Some(id2), "the newest for the next set's presims");
        assert_eq!(for_sim(&b, &r, Some(40), Some((40, 3))).map(|x| x.id), Some(id2));
        assert_eq!(for_sim(&b, &r, Some(40), Some((40, 2))).map(|x| x.id), Some(id), "the screen's second run of set 2");
        // another match never takes a record bound to this one
        assert!(for_sim(&b, &r, Some(41), Some((41, 1))).is_none());
        clear();
    }

    #[test]
    fn a_record_reads_back_from_the_save() {
        let mut r = full(11);
        r.choose("league_leona", 2, 1);
        r.reroll("league_garen", 0, 0, &marksman());
        r.used = true;
        r.bound = Some((7, 1));
        let text = encode(&r);
        let back = decode(&text, 7, 1, r.id).expect("decodes");
        assert_eq!(back.tiers, r.tiers);
        assert_eq!((back.blue.clone(), back.red.clone(), back.side), (r.blue.clone(), r.red.clone(), r.side));
        assert_eq!(back.mine, r.mine);
        assert!(back.used && back.bound == Some((7, 1)));
        assert!(decode("2|0|0000|||", 1, 1, 1).is_none());
        assert!(decode(&text.replace("league_leona=", "league_leona=x,y,z/"), 1, 1, 1).is_none());
        let unknown = text.replacen(AUGS[r.mine[0].picks[0].cards[0] as usize].key, "no_such_augment", 1);
        assert!(decode(&unknown, 1, 1, 1).is_none());
        assert_eq!(save_key(12, 3), "league_hextech:pick:12:3");
        assert!(by_key("deft").is_some());
    }
}
