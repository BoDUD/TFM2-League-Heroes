//! 彩蛋的规则（纯函数，单元测试用）：谁和谁对上、任务什么时候开始、谁赢、每次击杀 / 助攻给什么。
//!
//! 模拟里的东西（玩家、分路、击杀记录）由 `lib.rs` 换成这里的 [`Seat`]、[`Takedown`]，规则只看这些。

/// TFM2 的最高等级（league_aurelionsol 的 flight.rs、league_milio 的 rules.rs 也按 12 级换算）。
pub const MAX_LEVEL: usize = 12;
/// 英雄联盟的宿命任务在 18 级里的 16 级开始：按 1–12 级线性换算 1 + 15 × 11 / 17 = 10.7，取 11 级
/// （卡兹克的第三次进化也在 11 级：league_khazix 的 lv_r）。
pub const HUNT_LEVEL: usize = 11;
/// 弗雷尔卓德之战：全场击杀 + 助攻到这么多时开始。
pub const QUEEN_KA: usize = 20;
/// 警察抓小偷：每次击杀或助攻对面的金币。
pub const COP_GOLD: i64 = 1;
/// 时光老头与装甲熊：击杀对方的金币。
pub const BEAR_GOLD: i64 = 11;
/// 植物大战僵尸（婕拉 vs 赛恩）：击杀对方的金币。
pub const ZOMBIE_GOLD: i64 = 2;
/// 钓鱼执法：锤石每吸收一次赛娜的灵魂加的护甲、法强；赛娜 / 卢锡安每解放一次灵魂加的暴击（%）、射程。最多叠 `SOUL_CAP` 次。
pub const SOUL_DEF: i32 = 10;
pub const SOUL_AP: i32 = 15;
pub const SENNA_CRIT: i32 = 10;
pub const SENNA_RANGE: usize = 2_000;
pub const LUCIAN_CRIT: i32 = 5;
pub const LUCIAN_RANGE: usize = 1_000;
pub const SOUL_CAP: usize = 3;
/// 婕拉和茂凯同队、离得这么近时各加的移速（%：buff 只有百分比移速，没有固定值）。
pub const PLANTS_R: u64 = 60_000;
pub const PLANTS_MS: i32 = 1;
/// 熟女的魅力：每隔多久、多近、给多少（经验写不进去，给同样数目的金币，见 README）。
pub const CHARM_EVERY: usize = 300;
pub const CHARM_R: u64 = 60_000;
pub const CHARM_GOLD: i64 = 5;
/// 忍者的孤独：同队每多一个忍者，每个忍者少的最大生命。
pub const NINJA_HP: i32 = 1;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Hero {
    Rengar,
    Khazix,
    Ashe,
    Sejuani,
    Lissandra,
    Jinx,
    Caitlyn,
    Vi,
    Thresh,
    Senna,
    Lucian,
    Zilean,
    Volibear,
    Zyra,
    Sion,
    Maokai,
    Shen,
    Kennen,
    Akali,
    Zed,
    Nidalee,
    // 6 太阳镜防晒、9 鲨鱼吃小矮子（数据那一半在主包的莱昂娜、菲兹里）
    Leona,
    Fizz,
    Vayne,
    Locke,
    Heimerdinger,
    Ziggs,
    Twitch,
    LeeSin,
    Annie,
    Corki,
    Gnar,
    Kled,
    Lulu,
    Poppy,
    Rumble,
    Tristana,
    Veigar,
    Vex,
    Yuumi,
}

pub const HEROES: [Hero; 40] = [
    Hero::Rengar,
    Hero::Khazix,
    Hero::Ashe,
    Hero::Sejuani,
    Hero::Lissandra,
    Hero::Jinx,
    Hero::Caitlyn,
    Hero::Vi,
    Hero::Thresh,
    Hero::Senna,
    Hero::Lucian,
    Hero::Zilean,
    Hero::Volibear,
    Hero::Zyra,
    Hero::Sion,
    Hero::Maokai,
    Hero::Shen,
    Hero::Kennen,
    Hero::Akali,
    Hero::Zed,
    Hero::Nidalee,
    Hero::Leona,
    Hero::Fizz,
    Hero::Vayne,
    Hero::Locke,
    Hero::Heimerdinger,
    Hero::Ziggs,
    Hero::Twitch,
    Hero::LeeSin,
    Hero::Annie,
    Hero::Corki,
    Hero::Gnar,
    Hero::Kled,
    Hero::Lulu,
    Hero::Poppy,
    Hero::Rumble,
    Hero::Tristana,
    Hero::Veigar,
    Hero::Vex,
    Hero::Yuumi,
];

pub const QUEENS: [Hero; 3] = [Hero::Ashe, Hero::Sejuani, Hero::Lissandra];
pub const COPS: [Hero; 2] = [Hero::Caitlyn, Hero::Vi];
pub const NINJAS: [Hero; 4] = [Hero::Shen, Hero::Kennen, Hero::Akali, Hero::Zed];
/// 6 太阳镜防晒：我们的英雄里画上戴墨镜或护目镜遮住眼睛的（agent B 按 league/champions 的待机头像 x4 挑的：薇恩的红墨镜、洛克的
/// 粉墨镜、黑默丁格的蓝镜片护目镜、吉格斯的绿镜片护目镜、图奇的黄铜目镜，英雄联盟的原皮也戴着），加上李青的蒙眼布（用户自己举的
/// 例子）。不算：推到额头或帽子上的护目镜（伊泽瑞尔、崔丝塔娜、提莫、蔚、兰博、泽丽），透明眼镜（芙蕾雅），面具和面罩（烬、
/// 维克托、劫、慎），看不出戴眼镜的（库奇、辛吉德、卢锡安、格雷福斯）。
pub const SUNGLASSES: [Hero; 6] = [Hero::Vayne, Hero::Locke, Hero::Heimerdinger, Hero::Ziggs, Hero::Twitch, Hero::LeeSin];
/// 9 鲨鱼吃小矮子：鲨鱼吞得下的小约德尔人（用户的单子：安妮在英雄联盟的背景里是人类，但用户把她算作小个子）。提莫、黑默丁格
/// 留着尸体（用户：太重 / 头太大）。阿木木不是约德尔人。
pub const SWALLOWED: [Hero; 13] = [
    Hero::Annie,
    Hero::Corki,
    Hero::Gnar,
    Hero::Kennen,
    Hero::Kled,
    Hero::Lulu,
    Hero::Poppy,
    Hero::Rumble,
    Hero::Tristana,
    Hero::Veigar,
    Hero::Vex,
    Hero::Yuumi,
    Hero::Ziggs,
];

impl Hero {
    /// The champion id in the main pack (`entity.name()`).
    pub fn id(self) -> &'static str {
        match self {
            Hero::Rengar => "league_rengar",
            Hero::Khazix => "league_khazix",
            Hero::Ashe => "league_ashe",
            Hero::Sejuani => "league_sejuani",
            Hero::Lissandra => "league_lissandra",
            Hero::Jinx => "league_jinx",
            Hero::Caitlyn => "league_caitlyn",
            Hero::Vi => "league_vi",
            Hero::Thresh => "league_thresh",
            Hero::Senna => "league_senna",
            Hero::Lucian => "league_lucian",
            Hero::Zilean => "league_zilean",
            Hero::Volibear => "league_volibear",
            Hero::Zyra => "league_zyra",
            Hero::Sion => "league_sion",
            Hero::Maokai => "league_maokai",
            Hero::Shen => "league_shen",
            Hero::Kennen => "league_kennen",
            Hero::Akali => "league_akali",
            Hero::Zed => "league_zed",
            Hero::Nidalee => "league_nidalee",
            Hero::Leona => "league_leona",
            Hero::Fizz => "league_fizz",
            Hero::Vayne => "league_vayne",
            Hero::Locke => "league_locke",
            Hero::Heimerdinger => "league_heimerdinger",
            Hero::Ziggs => "league_ziggs",
            Hero::Twitch => "league_twitch",
            Hero::LeeSin => "league_leesin",
            Hero::Annie => "league_annie",
            Hero::Corki => "league_corki",
            Hero::Gnar => "league_gnar",
            Hero::Kled => "league_kled",
            Hero::Lulu => "league_lulu",
            Hero::Poppy => "league_poppy",
            Hero::Rumble => "league_rumble",
            Hero::Tristana => "league_tristana",
            Hero::Veigar => "league_veigar",
            Hero::Vex => "league_vex",
            Hero::Yuumi => "league_yuumi",
        }
    }

    pub fn of(id: &str) -> Option<Hero> {
        HEROES.iter().copied().find(|h| h.id() == id)
    }
}

/// 一名选手：玩家编号、队伍、英雄（只记彩蛋里的英雄）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Seat {
    pub player: usize,
    pub team: usize,
    pub hero: Hero,
}

/// 击杀记录的一条，换成玩家编号：谁死了、谁杀的、谁助攻。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Takedown {
    pub tick: usize,
    pub victim: usize,
    pub killer: Option<usize>,
    pub assists: Vec<usize>,
}

impl Takedown {
    /// 这个玩家击杀或助攻了这一次。
    pub fn by(&self, player: usize) -> bool {
        self.killer == Some(player) || self.assists.contains(&player)
    }
}

pub fn seats(cast: &[Seat], hero: Hero) -> Vec<Seat> {
    cast.iter().copied().filter(|s| s.hero == hero).collect()
}

fn hero_of(cast: &[Seat], player: usize) -> Option<Seat> {
    cast.iter().copied().find(|s| s.player == player)
}

// ===================== 一、宿命对决 =====================

/// 1 狩猎开始：雷恩加尔和卡兹克在对面两队 -> (雷恩加尔, 卡兹克) 的玩家编号。
pub fn hunt_pair(cast: &[Seat]) -> Option<(usize, usize)> {
    let r = seats(cast, Hero::Rengar);
    let k = seats(cast, Hero::Khazix);
    r.iter().find_map(|a| k.iter().find(|b| b.team != a.team).map(|b| (a.player, b.player)))
}

/// 两个都到了任务的等级。
pub fn hunt_on(levels: (usize, usize)) -> bool {
    levels.0 >= HUNT_LEVEL && levels.1 >= HUNT_LEVEL
}

/// 任务开始后的一次击杀：谁击杀或助攻了另一个 -> 赢家。
pub fn hunt_winner(td: &Takedown, pair: (usize, usize)) -> Option<usize> {
    let (r, k) = pair;
    if td.victim == k && td.by(r) {
        Some(r)
    } else if td.victim == r && td.by(k) {
        Some(k)
    } else {
        None
    }
}

/// 2 弗雷尔卓德之战：有一名对面的女王的那些女王（艾希、瑟庄妮、丽桑卓里至少两个分在两队；否则空的）。
pub fn queens(cast: &[Seat]) -> Vec<Seat> {
    let q: Vec<Seat> = cast.iter().copied().filter(|s| QUEENS.contains(&s.hero)).collect();
    q.iter().copied().filter(|a| q.iter().any(|b| b.team != a.team)).collect()
}

pub fn queens_on(total_ka: usize) -> bool {
    total_ka >= QUEEN_KA
}

/// 任务开始后的一次击杀：死的是女王，击杀者是对面的女王就是她，否则助攻里第一个对面的女王。
pub fn queen_winner(td: &Takedown, queens: &[Seat]) -> Option<usize> {
    let victim = queens.iter().find(|q| q.player == td.victim)?;
    let rival = |p: usize| queens.iter().any(|q| q.player == p && q.team != victim.team);
    td.killer.filter(|&p| rival(p)).or_else(|| td.assists.iter().copied().find(|&p| rival(p)))
}

/// 3 警察抓小偷：金克丝和对面的凯特琳 / 蔚。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Chase {
    /// 有对面警察的金克丝。
    pub robbers: Vec<Seat>,
    /// 有对面金克丝的凯特琳、蔚。
    pub cops: Vec<Seat>,
}

pub fn chase(cast: &[Seat]) -> Option<Chase> {
    let jinx = seats(cast, Hero::Jinx);
    let cops: Vec<Seat> = cast.iter().copied().filter(|s| COPS.contains(&s.hero)).collect();
    let c = Chase {
        robbers: jinx.iter().copied().filter(|j| cops.iter().any(|c| c.team != j.team)).collect(),
        cops: cops.iter().copied().filter(|c| jinx.iter().any(|j| j.team != c.team)).collect(),
    };
    (!c.robbers.is_empty()).then_some(c)
}

/// 一次击杀里记上一笔的人（每人 +1、+`COP_GOLD` 金币）：死的是金克丝，参与的对面警察各一笔（抓捕的罪犯）；死的是警察，
/// 参与的对面金克丝一笔（甩掉的条子）。
pub fn arrests(td: &Takedown, c: &Chase) -> Vec<usize> {
    if let Some(r) = c.robbers.iter().find(|r| r.player == td.victim) {
        return c.cops.iter().filter(|k| k.team != r.team && td.by(k.player)).map(|k| k.player).collect();
    }
    if let Some(k) = c.cops.iter().find(|k| k.player == td.victim) {
        return c.robbers.iter().filter(|r| r.team != k.team && td.by(r.player)).map(|r| r.player).collect();
    }
    Vec::new()
}

/// 4 钓鱼执法：锤石和对面的赛娜 / 卢锡安。
pub fn fishing(cast: &[Seat]) -> Option<(Vec<Seat>, Vec<Seat>)> {
    let thresh = seats(cast, Hero::Thresh);
    let others: Vec<Seat> = cast.iter().copied().filter(|s| matches!(s.hero, Hero::Senna | Hero::Lucian)).collect();
    let t: Vec<Seat> = thresh.iter().copied().filter(|a| others.iter().any(|b| b.team != a.team)).collect();
    let o: Vec<Seat> = others.iter().copied().filter(|b| thresh.iter().any(|a| a.team != b.team)).collect();
    (!t.is_empty()).then_some((t, o))
}

/// 灵魂的去向。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Soul {
    /// 锤石杀了赛娜：吸收她的灵魂。
    Taken,
    /// 赛娜杀了锤石：解放灵魂。
    FreedBySenna,
    /// 卢锡安杀了锤石：解放灵魂（少一些）。
    FreedByLucian,
}

/// 一次击杀（只算击杀者）：(得到的人, 怎么得的)。
pub fn soul_event(td: &Takedown, cast: &[Seat]) -> Option<(usize, Soul)> {
    let killer = hero_of(cast, td.killer?)?;
    let victim = hero_of(cast, td.victim)?;
    if killer.team == victim.team {
        return None;
    }
    match (killer.hero, victim.hero) {
        (Hero::Thresh, Hero::Senna) => Some((killer.player, Soul::Taken)),
        (Hero::Senna, Hero::Thresh) => Some((killer.player, Soul::FreedBySenna)),
        (Hero::Lucian, Hero::Thresh) => Some((killer.player, Soul::FreedByLucian)),
        _ => None,
    }
}

/// 叠了 `stacks` 层的属性：锤石 (护甲, 法强)，赛娜 / 卢锡安 (暴击 %, 射程)。
pub fn soul_stats(kind: Soul, stacks: usize) -> (i32, i32, i32, usize) {
    let n = stacks.min(SOUL_CAP);
    match kind {
        Soul::Taken => (SOUL_DEF * n as i32, SOUL_AP * n as i32, 0, 0),
        Soul::FreedBySenna => (0, 0, SENNA_CRIT * n as i32, SENNA_RANGE * n),
        Soul::FreedByLucian => (0, 0, LUCIAN_CRIT * n as i32, LUCIAN_RANGE * n),
    }
}

/// 5 时光老头与装甲熊、7 植物大战僵尸（婕拉 vs 赛恩）：`a`、`b` 在对面两队时，一个击杀另一个 -> (击杀者, 金币)。只算击杀。
pub fn bounty(td: &Takedown, cast: &[Seat], a: Hero, b: Hero, gold: i64) -> Option<(usize, i64)> {
    let killer = hero_of(cast, td.killer?)?;
    let victim = hero_of(cast, td.victim)?;
    let pair = (killer.hero == a && victim.hero == b) || (killer.hero == b && victim.hero == a);
    (pair && killer.team != victim.team).then_some((killer.player, gold))
}

/// 两个英雄在对面两队（基兰 / 沃利贝尔、婕拉 / 赛恩）：(a 的玩家, b 的玩家)。
pub fn rivals(cast: &[Seat], a: Hero, b: Hero) -> Option<(usize, usize)> {
    let x = seats(cast, a);
    let y = seats(cast, b);
    x.iter().find_map(|p| y.iter().find(|q| q.team != p.team).map(|q| (p.player, q.player)))
}

// ===================== 二、趣味属性互动 =====================

/// 7 婕拉和茂凯同队：(婕拉, 茂凯)。
pub fn plant_pair(cast: &[Seat]) -> Option<(usize, usize)> {
    let z = seats(cast, Hero::Zyra);
    let m = seats(cast, Hero::Maokai);
    z.iter().find_map(|a| m.iter().find(|b| b.team == a.team).map(|b| (a.player, b.player)))
}

/// 两个都活着、离得够近。
pub fn plants_near(alive: (bool, bool), dist_sq: u64) -> bool {
    alive.0 && alive.1 && dist_sq <= PLANTS_R * PLANTS_R
}

/// 8 忍者的孤独：每个忍者少的最大生命（同队有 n 个忍者时各少 n - 1；只有一个时不在表里）。
pub fn ninja_hp(cast: &[Seat]) -> Vec<(usize, i32)> {
    let ninjas: Vec<Seat> = cast.iter().copied().filter(|s| NINJAS.contains(&s.hero)).collect();
    ninjas
        .iter()
        .filter_map(|a| {
            let others = ninjas.iter().filter(|b| b.team == a.team && b.player != a.player).count() as i32;
            (others > 0).then_some((a.player, -NINJA_HP * others))
        })
        .collect()
}

/// 11 熟女的魅力：这一 tick 该发了（开局后每 `CHARM_EVERY` tick）。
pub fn charm_due(tick: usize) -> bool {
    tick > 0 && tick % CHARM_EVERY == 0
}

/// 身边的一名队友：(玩家, 等级, 活着, 离她的距离平方)。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Near {
    pub player: usize,
    pub level: usize,
    pub alive: bool,
    pub dist_sq: u64,
}

/// 美洲狮形态的她身边、等级比她低的活着的队友。
pub fn charmed(her_level: usize, cougar: bool, allies: &[Near]) -> Vec<usize> {
    if !cougar {
        return Vec::new();
    }
    allies.iter().filter(|a| a.alive && a.level < her_level && a.dist_sq <= CHARM_R * CHARM_R).map(|a| a.player).collect()
}

/// 6 太阳镜防晒：对面有莱昂娜的戴墨镜的英雄（玩家）。
pub fn shaded(cast: &[Seat]) -> Vec<usize> {
    let leona = seats(cast, Hero::Leona);
    cast.iter().filter(|s| SUNGLASSES.contains(&s.hero) && leona.iter().any(|l| l.team != s.team)).map(|s| s.player).collect()
}

/// 9 鲨鱼吃小矮子：对面有菲兹的小约德尔人（玩家）。
pub fn prey(cast: &[Seat]) -> Vec<usize> {
    let fizz = seats(cast, Hero::Fizz);
    cast.iter().filter(|s| SWALLOWED.contains(&s.hero) && fizz.iter().any(|f| f.team != s.team)).map(|s| s.player).collect()
}

/// 这一局开了哪些彩蛋（开局按阵容定）。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Active {
    pub hunt: Option<(usize, usize)>,
    pub queens: Vec<Seat>,
    pub chase: Option<Chase>,
    pub fishing: Option<(Vec<Seat>, Vec<Seat>)>,
    pub bears: Option<(usize, usize)>,
    pub zombies: Option<(usize, usize)>,
    pub plants: Option<(usize, usize)>,
    pub ninjas: Vec<(usize, i32)>,
    pub nidalee: Vec<Seat>,
    /// 6 对面有莱昂娜的戴墨镜的玩家；9 对面有菲兹的小约德尔人。
    pub shades: Vec<usize>,
    pub prey: Vec<usize>,
}

impl Active {
    pub fn of(cast: &[Seat]) -> Active {
        Active {
            hunt: hunt_pair(cast),
            queens: queens(cast),
            chase: chase(cast),
            fishing: fishing(cast),
            bears: rivals(cast, Hero::Zilean, Hero::Volibear),
            zombies: rivals(cast, Hero::Zyra, Hero::Sion),
            plants: plant_pair(cast),
            ninjas: ninja_hp(cast),
            nidalee: seats(cast, Hero::Nidalee),
            shades: shaded(cast),
            prey: prey(cast),
        }
    }

    pub fn any(&self) -> bool {
        *self != Active::default()
    }

    /// One word an egg for the log line.
    pub fn names(&self) -> Vec<&'static str> {
        let mut v = Vec::new();
        if self.hunt.is_some() {
            v.push("hunt");
        }
        if !self.queens.is_empty() {
            v.push("queens");
        }
        if self.chase.is_some() {
            v.push("cops");
        }
        if self.fishing.is_some() {
            v.push("souls");
        }
        if self.bears.is_some() {
            v.push("bears");
        }
        if self.zombies.is_some() {
            v.push("zombies");
        }
        if self.plants.is_some() {
            v.push("plants");
        }
        if !self.ninjas.is_empty() {
            v.push("ninjas");
        }
        if !self.nidalee.is_empty() {
            v.push("charm");
        }
        if !self.shades.is_empty() {
            v.push("shades");
        }
        if !self.prey.is_empty() {
            v.push("shark");
        }
        v
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn s(player: usize, team: usize, hero: Hero) -> Seat {
        Seat { player, team, hero }
    }

    fn td(victim: usize, killer: Option<usize>, assists: &[usize]) -> Takedown {
        Takedown { tick: 100, victim, killer, assists: assists.to_vec() }
    }

    #[test]
    fn every_hero_id_reads_back() {
        for h in HEROES {
            assert_eq!(Hero::of(h.id()), Some(h));
        }
        assert_eq!(Hero::of("league_garen"), None);
    }

    #[test]
    fn the_stage_is_level_11_of_12() {
        // League's 16 of 18 on TFM2's 12 levels
        assert_eq!((1.0 + 15.0 * (MAX_LEVEL - 1) as f64 / 17.0_f64).round() as usize, HUNT_LEVEL);
        assert!(hunt_on((11, 11)) && hunt_on((12, 11)));
        assert!(!hunt_on((10, 12)) && !hunt_on((12, 10)));
    }

    #[test]
    fn the_hunt_needs_them_on_opposing_teams() {
        assert_eq!(hunt_pair(&[s(1, 0, Hero::Rengar), s(6, 1, Hero::Khazix)]), Some((1, 6)));
        assert_eq!(hunt_pair(&[s(1, 0, Hero::Rengar), s(2, 0, Hero::Khazix)]), None);
        assert_eq!(hunt_pair(&[s(1, 0, Hero::Rengar)]), None);
    }

    #[test]
    fn the_first_kill_or_assist_on_the_other_wins_the_hunt() {
        let pair = (1, 6);
        assert_eq!(hunt_winner(&td(6, Some(1), &[]), pair), Some(1));
        assert_eq!(hunt_winner(&td(6, Some(2), &[1]), pair), Some(1)); // an assist counts
        assert_eq!(hunt_winner(&td(1, Some(7), &[6, 8]), pair), Some(6));
        assert_eq!(hunt_winner(&td(1, Some(7), &[8]), pair), None); // Kha'Zix not in it
        assert_eq!(hunt_winner(&td(3, Some(6), &[]), pair), None); // another victim
    }

    #[test]
    fn queens_need_a_queen_across() {
        let all = [s(0, 0, Hero::Ashe), s(1, 0, Hero::Sejuani), s(7, 1, Hero::Lissandra)];
        assert_eq!(queens(&all).len(), 3);
        assert!(queens(&[s(0, 0, Hero::Ashe), s(1, 0, Hero::Sejuani)]).is_empty());
        assert!(queens(&[s(0, 0, Hero::Ashe)]).is_empty());
        assert!(!queens_on(19) && queens_on(20));
    }

    #[test]
    fn the_queen_is_the_killer_or_the_first_assisting_rival_queen() {
        let q = [s(0, 0, Hero::Ashe), s(1, 0, Hero::Sejuani), s(7, 1, Hero::Lissandra)];
        assert_eq!(queen_winner(&td(7, Some(0), &[1]), &q), Some(0));
        assert_eq!(queen_winner(&td(7, Some(3), &[1, 0]), &q), Some(1));
        assert_eq!(queen_winner(&td(0, Some(7), &[]), &q), Some(7));
        // her own team's queen cannot win on her; a non-queen victim wins nothing
        assert_eq!(queen_winner(&td(0, Some(5), &[1]), &q), None);
        assert_eq!(queen_winner(&td(5, Some(0), &[]), &q), None);
    }

    #[test]
    fn cops_count_takedowns_both_ways() {
        let cast = [s(3, 0, Hero::Jinx), s(8, 1, Hero::Caitlyn), s(9, 1, Hero::Vi)];
        let c = chase(&cast).expect("a chase");
        assert_eq!(c.cops.len(), 2);
        // Jinx down: every cop in it
        assert_eq!(arrests(&td(3, Some(8), &[9]), &c), vec![8, 9]);
        assert_eq!(arrests(&td(3, Some(5), &[9]), &c), vec![9]);
        // a cop down by Jinx (an assist counts too)
        assert_eq!(arrests(&td(8, Some(4), &[3]), &c), vec![3]);
        assert!(arrests(&td(8, Some(4), &[]), &c).is_empty());
        assert!(arrests(&td(5, Some(3), &[]), &c).is_empty());
    }

    #[test]
    fn a_cop_on_jinx_s_own_team_is_no_cop() {
        let cast = [s(3, 0, Hero::Jinx), s(2, 0, Hero::Vi), s(8, 1, Hero::Caitlyn)];
        let c = chase(&cast).expect("a chase");
        assert_eq!(c.cops, vec![s(8, 1, Hero::Caitlyn)]);
        assert!(chase(&[s(3, 0, Hero::Jinx), s(2, 0, Hero::Vi)]).is_none());
        assert!(chase(&[s(8, 1, Hero::Caitlyn)]).is_none());
    }

    #[test]
    fn souls_go_by_the_killer() {
        let cast = [s(4, 0, Hero::Thresh), s(8, 1, Hero::Senna), s(9, 1, Hero::Lucian)];
        assert!(fishing(&cast).is_some());
        assert_eq!(soul_event(&td(8, Some(4), &[]), &cast), Some((4, Soul::Taken)));
        assert_eq!(soul_event(&td(4, Some(8), &[]), &cast), Some((8, Soul::FreedBySenna)));
        assert_eq!(soul_event(&td(4, Some(9), &[8]), &cast), Some((9, Soul::FreedByLucian)));
        // an assist is not a kill; Thresh killing Lucian takes no soul
        assert_eq!(soul_event(&td(8, Some(2), &[4]), &cast), None);
        assert_eq!(soul_event(&td(9, Some(4), &[]), &cast), None);
        assert!(fishing(&[s(4, 0, Hero::Thresh), s(1, 0, Hero::Senna)]).is_none());
    }

    #[test]
    fn soul_stats_stack_to_the_cap() {
        assert_eq!(soul_stats(Soul::Taken, 1), (SOUL_DEF, SOUL_AP, 0, 0));
        assert_eq!(soul_stats(Soul::Taken, 5), (SOUL_DEF * 3, SOUL_AP * 3, 0, 0));
        assert_eq!(soul_stats(Soul::FreedBySenna, 2), (0, 0, 2 * SENNA_CRIT, 2 * SENNA_RANGE));
        // Lucian's is the smaller one
        let (_, _, c, r) = soul_stats(Soul::FreedByLucian, 1);
        assert!(c < SENNA_CRIT && r < SENNA_RANGE);
    }

    #[test]
    fn bounties_pay_the_killer_only() {
        let cast = [s(2, 0, Hero::Zilean), s(6, 1, Hero::Volibear), s(1, 0, Hero::Zyra), s(5, 1, Hero::Sion)];
        assert_eq!(bounty(&td(6, Some(2), &[]), &cast, Hero::Zilean, Hero::Volibear, BEAR_GOLD), Some((2, 11)));
        assert_eq!(bounty(&td(2, Some(6), &[]), &cast, Hero::Zilean, Hero::Volibear, BEAR_GOLD), Some((6, 11)));
        assert_eq!(bounty(&td(6, Some(1), &[2]), &cast, Hero::Zilean, Hero::Volibear, BEAR_GOLD), None);
        assert_eq!(bounty(&td(5, Some(1), &[]), &cast, Hero::Zyra, Hero::Sion, ZOMBIE_GOLD), Some((1, 2)));
        assert_eq!(bounty(&td(1, Some(5), &[]), &cast, Hero::Zyra, Hero::Sion, ZOMBIE_GOLD), Some((5, 2)));
        assert_eq!(rivals(&cast, Hero::Zilean, Hero::Volibear), Some((2, 6)));
        assert_eq!(rivals(&[s(2, 0, Hero::Zilean), s(3, 0, Hero::Volibear)], Hero::Zilean, Hero::Volibear), None);
    }

    #[test]
    fn plants_walk_together_on_one_team() {
        assert_eq!(plant_pair(&[s(1, 0, Hero::Zyra), s(3, 0, Hero::Maokai)]), Some((1, 3)));
        assert_eq!(plant_pair(&[s(1, 0, Hero::Zyra), s(8, 1, Hero::Maokai)]), None);
        assert!(plants_near((true, true), PLANTS_R * PLANTS_R));
        assert!(!plants_near((true, true), PLANTS_R * PLANTS_R + 1));
        assert!(!plants_near((true, false), 0));
    }

    #[test]
    fn ninjas_lose_one_max_health_per_other_ninja() {
        let cast = [s(0, 0, Hero::Shen), s(1, 0, Hero::Zed), s(2, 0, Hero::Akali), s(7, 1, Hero::Kennen)];
        let mut hp = ninja_hp(&cast);
        hp.sort();
        assert_eq!(hp, vec![(0, -2), (1, -2), (2, -2)]); // Kennen alone on his team: untouched
        assert!(ninja_hp(&[s(0, 0, Hero::Shen), s(7, 1, Hero::Zed)]).is_empty());
    }

    #[test]
    fn the_cougar_charms_lower_level_allies_near_her() {
        let near = |player, level, dist: u64| Near { player, level, alive: true, dist_sq: dist * dist };
        let allies = [near(1, 6, 10_000), near(2, 8, 10_000), near(3, 5, CHARM_R + 1), near(4, 7, CHARM_R)];
        assert_eq!(charmed(8, true, &allies), vec![1, 4]);
        assert!(charmed(8, false, &allies).is_empty());
        let dead = Near { alive: false, ..near(1, 1, 0) };
        assert!(charmed(8, true, &[dead]).is_empty());
        assert!(!charm_due(0) && charm_due(CHARM_EVERY) && !charm_due(CHARM_EVERY + 1));
    }

    #[test]
    fn sunglasses_only_against_a_leona_across() {
        let cast = [s(0, 0, Hero::Leona), s(1, 0, Hero::Vayne), s(6, 1, Hero::LeeSin), s(7, 1, Hero::Ziggs), s(8, 1, Hero::Zed)];
        assert_eq!(shaded(&cast), vec![6, 7]); // Vayne is on Leona's own team; Zed's mask is no sunglasses
        assert!(shaded(&[s(1, 0, Hero::Vayne), s(6, 1, Hero::Twitch)]).is_empty(), "no Leona");
        assert_eq!(SUNGLASSES.len(), 6);
    }

    #[test]
    fn the_shark_hunts_the_yordles_across() {
        let cast = [s(0, 0, Hero::Fizz), s(1, 0, Hero::Lulu), s(5, 1, Hero::Kennen), s(6, 1, Hero::Ziggs), s(7, 1, Hero::Heimerdinger)];
        assert_eq!(prey(&cast), vec![5, 6]); // Lulu is his ally; Heimerdinger's head is too big
        assert!(prey(&[s(1, 0, Hero::Lulu), s(5, 1, Hero::Annie)]).is_empty(), "no Fizz");
        assert!(!SWALLOWED.contains(&Hero::Heimerdinger));
    }

    #[test]
    fn the_cast_turns_on_its_eggs() {
        let cast = [s(0, 0, Hero::Rengar), s(5, 1, Hero::Khazix), s(1, 0, Hero::Nidalee)];
        let a = Active::of(&cast);
        assert_eq!(a.names(), vec!["hunt", "charm"]);
        assert!(a.any());
        assert!(!Active::of(&[]).any());
        let b = Active::of(&[s(0, 0, Hero::Leona), s(5, 1, Hero::Vayne), s(1, 0, Hero::Fizz), s(6, 1, Hero::Tristana)]);
        assert_eq!(b.names(), vec!["shades", "shark"]);
        // a wearer or a yordle alone turns nothing on
        assert!(!Active::of(&[s(5, 1, Hero::Vayne), s(6, 1, Hero::Tristana)]).any());
    }
}
