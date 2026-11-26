//! 触发类海克斯（0.3.0，第 3 步，用户 2026-11-26：「做第 3 步」「还有触发特效也要做吧」）：比赛钩子每 [`EVERY`] tick 看一次场上，
//! 按每个人拿着的触发类海克斯（[`super::augments::Ev`]）出效果。都只读模拟、只按 tick 算，两份预演和屏幕上那份一模一样。
//!
//! 看的是这几样（每样都只和上一次比，同一条命）：
//!
//! - **打中英雄**：他的伤害统计 `deal` 涨了，同时他身边（[`REACH`]）有敌方英雄的生命 + 护盾掉了（大小龙的龙魂同一个做法）；读不到
//!   统计时看他刚出没出手。被打的人按远近排，最多算 3 个。本包替他打出的伤害下一次不算（不然自己触发自己）。
//! - **放技能 / 普攻**：四个冷却（普攻、技能、技能 2、大招）一下子涨上去。
//! - **参与击杀**：游戏的击杀记录（击杀者、助攻按队伍 + 分路认座位）。
//! - **残血**：生命从线上掉到线下的那一次（35%、40%、15%）。
//! - **控住敌人**：他刚放过技能（[`CC_WINDOW`] 以内），身边的敌方英雄刚挂上眩晕、击飞、定身、嘲讽、恐惧、魅惑（自己的施法动作、
//!   位移不算；本包的雪球击飞也不算）。同一时刻队友也控了人的话分不清是谁，按都算。
//! - **定时**：冷却到了、射程里有目标就放。
//!
//! 伤害走游戏自己的结算（`deal_damage_typed`：护甲魔抗、统计、击杀都算他的）；回血、护盾、减速、击飞也都是游戏的接口。限时的效果是
//! 带名字的限时 buff（`league_hextech_e:<名字>`），叠层的是 `league_hextech_s:<名字>`（坦克引擎、惊世邪恶：层数跟着人走，复活后
//! 补回），体型的档是 `league_hextech_g:<名字>`（高清帧引擎按 buff 名放大身体，[`super::hd`]）。
//!
//! 屏幕放的那场模拟里每次触发记一条特效（[`Out`]，lib.rs 放进 [`super::feed`]），客户端按屏幕时钟画（[`super::fx`]）；预演、后台
//! 比赛不记，模拟从来不读它。

use mod_api_stable::*;

use super::augments::{Ev, EV_N};

/// 每这么多 tick 看一次。
pub const EVERY: usize = 2;
/// 离敌方英雄这么近才读伤害统计（远程普攻 60000 加两个身体：大小龙同一个数）。
pub const REACH: u64 = 85_000;
/// 放技能后这么久以内敌人挂上控制，算他控住的。
pub const CC_WINDOW: usize = 45;
/// 读不到伤害统计时：出手后这么久以内身边敌方英雄掉血算他打的。
const ACTION_WINDOW: usize = 45;
/// 冷却涨这么多算放了（普攻、技能、技能 2、大招）。
const JUMP: [usize; 4] = [4, 20, 20, 60];
/// 一次命中最多算几个被打的人。
const VICTIMS: usize = 3;

// ===================== 数值（海克斯的说明照这些写） =====================

// 银
pub const FIREBRAND_PULSES: u8 = 6;
pub const FIREBRAND_EVERY: usize = 30;
pub fn firebrand_total(vmax: usize, ad: usize, ap: usize) -> usize {
    30 + vmax * 3 / 100 + ad * 10 / 100 + ap * 10 / 100
}
pub const ICE_SLOW: i32 = 20;
pub const ICE_T: usize = 90;
pub const LIGHT_EVERY: u32 = 4;
/// 两次命中隔这么久以上才算两次（一下 AOE 打到几个人只算一次）。
pub const LIGHT_GAP: usize = 20;
pub fn light_damage(ad: usize) -> usize {
    25 + ad * 40 / 100
}
pub const ESCAPE_PCT: usize = 35;
pub const ESCAPE_SHIELD_T: usize = 180;
pub const ESCAPE_MS: i32 = 40;
pub const ESCAPE_MS_T: usize = 120;
pub const ESCAPE_CD: usize = 2_700;
pub fn escape_shield(max: usize) -> usize {
    100 + max * 12 / 100
}
pub const TANK_MOST: u8 = 12;
pub const TANK_HP: i32 = 30;
pub const TANK_RES: i32 = 3;
/// 这么多层起体型大一档、两档。
pub const TANK_BIG: [u8; 2] = [6, 12];
pub const PUNCH_TICKS: usize = 24;
pub const HEAVY_PCT: usize = 3;
pub const HEAVY_GAP: usize = 30;
pub const MISSILE_CD: usize = 120;
pub const MISSILE_RANGE: u64 = 75_000;
/// 飞弹一 tick 飞多远（最少飞 [`MISSILE_MIN_T`] tick）。
pub const MISSILE_SPEED: u64 = 4_000;
pub const MISSILE_MIN_T: usize = 8;
pub fn missile_damage(ap: usize, ad: usize) -> usize {
    30 + ap * 25 / 100 + ad * 10 / 100
}

// 金
pub const CHAIN_CD: usize = 180;
pub const CHAIN_R: u64 = 40_000;
pub const CHAIN_TARGETS: usize = 3;
pub const CHAIN_SLOW: i32 = 30;
pub const CHAIN_SLOW_T: usize = 30;
pub fn chain_damage(ad: usize, ap: usize) -> usize {
    40 + ad * 25 / 100 + ap * 30 / 100
}
pub const VULN_AMP: usize = 10;
pub const VULN_T: usize = 180;
pub const ETHER_T: usize = 180;
pub fn ether_damage(ap: usize, ad: usize) -> usize {
    40 + ap * 35 / 100 + ad * 25 / 100
}
pub const COLOSSUS_T: usize = 150;
pub const COLOSSUS_CD: usize = 300;
pub const CC_REACH: u64 = 90_000;
pub fn colossus_shield(max: usize) -> usize {
    80 + max * 10 / 100
}
pub const EXEC_PCT: usize = 30;
pub const EXEC_DMG_PCT: usize = 5;
pub const EXEC_GAP: usize = 30;
pub const DAWN_PCT: usize = 40;
pub const DAWN_HEAL_PCT: usize = 30;
pub const DAWN_PULSES: u8 = 4;
pub const HOT_EVERY: usize = 30;
pub const DAWN_CD: usize = 3_000;
pub const EXCITED_AS: i32 = 50;
pub const EXCITED_MS: i32 = 25;
pub const EXCITED_T: usize = 300;
pub const GUARD_PCT: usize = 40;
pub const GUARD_R: u64 = 60_000;
pub const GUARD_T: usize = 150;
pub const GUARD_CD: usize = 720;
pub fn guard_shield(holder_max: usize) -> usize {
    80 + holder_max * 8 / 100
}
pub const EVIL_AP: i32 = 2;
pub const EVIL_MOST: u16 = 75;
pub const EVIL_GAP: usize = 60;

// 棱彩
pub const LASER_CD: usize = 600;
pub const LASER_RANGE: u64 = 90_000;
pub const LASER_DELAY: usize = 45;
pub const LASER_R: u64 = 22_000;
pub fn laser_base(ap: usize, ad: usize) -> usize {
    100 + ap * 40 / 100 + ad * 30 / 100
}
pub const LASER_HP_PCT: usize = 6;
pub const COMET_DELAY: usize = 30;
pub const COMET_R: u64 = 18_000;
pub const COMET_CD: usize = 240;
pub fn comet_base(ap: usize, ad: usize) -> usize {
    80 + ap * 35 / 100 + ad * 25 / 100
}
pub const COMET_HP_PCT: usize = 4;
pub const FINAL_T: usize = 300;
pub const FINAL_AS: i32 = 30;
pub const FINAL_MS: i32 = 20;
pub const FINAL_REDUCE: usize = 20;
pub const FINAL_TENACITY: usize = 80;
pub const SNOW_CD: usize = 720;
pub const SNOW_RANGE: u64 = 85_000;
pub const SNOW_T: usize = 36;
pub const SNOW_R: u64 = 20_000;
pub const SNOW_AIR: u64 = 45;
pub fn snow_base(ad: usize, ap: usize) -> usize {
    60 + ad * 30 / 100 + ap * 20 / 100
}
pub const SNOW_HP_PCT: usize = 4;
pub const QUANTUM_CD: usize = 480;
pub const QUANTUM_R: u64 = 26_000;
pub fn quantum_base(ad: usize) -> usize {
    40 + ad * 45 / 100
}
pub const QUANTUM_HP_PCT: usize = 6;
pub const QUANTUM_HEAL_PCT: usize = 4;
pub const UNDYING_PCT: usize = 15;
pub const UNDYING_T: usize = 120;
pub const UNDYING_HEAL_PCT: usize = 20;
pub const UNDYING_PULSES: u8 = 4;
pub const UNDYING_CD: usize = 5_400;
pub const IMMOLATE_EVERY: usize = 60;
pub const IMMOLATE_R: u64 = 22_000;
pub fn immolate_damage(holder_max: usize) -> usize {
    15 + holder_max * 15 / 1000
}
pub const TYPHOON_CD: usize = 40;
pub const TYPHOON_R: u64 = 50_000;
pub const TYPHOON_TARGETS: usize = 2;
pub fn typhoon_damage(ad: usize, ap: usize) -> usize {
    ad * 25 / 100 + ap * 10 / 100
}
pub const WARD_CD: usize = 480;
pub const WARD_R: u64 = 70_000;
/// 生命比例低于这么多的才给（满血的人不浪费）。
pub const WARD_BELOW_PCT: usize = 85;
pub const WARD_T: usize = 180;
pub const WARD_MS: i32 = 20;
pub const WARD_MS_T: usize = 120;
pub fn ward_shield(holder_ap: usize, ally_max: usize) -> usize {
    100 + holder_ap * 25 / 100 + ally_max * 8 / 100
}

// ===================== buff 名 =====================

pub const E_ICE: &str = "league_hextech_e:ice_cold";
pub const E_CHAIN: &str = "league_hextech_e:chain_slow";
pub const E_VULN: &str = "league_hextech_e:vulnerability";
pub const E_ESCAPE: &str = "league_hextech_e:escape_plan";
pub const E_EXCITED: &str = "league_hextech_e:get_excited";
pub const E_FINAL: &str = "league_hextech_e:final_form";
pub const E_UNDYING: &str = "league_hextech_e:undying_will";
pub const E_WARD: &str = "league_hextech_e:sacred_ward";
pub const S_TANK: &str = "league_hextech_s:tank_engine";
pub const S_EVIL: &str = "league_hextech_s:phenomenal_evil";
pub const G_TANK: [&str; 2] = ["league_hextech_g:tank_engine_1", "league_hextech_g:tank_engine_2"];

fn timed(name: &str, ticks: usize, f: impl FnOnce(&mut BuffV1)) -> BuffV1 {
    let mut b = BuffV1::timed(name, ticks);
    f(&mut b);
    b
}

pub fn ice_slow() -> BuffV1 {
    timed(E_ICE, ICE_T, |b| b.move_speed_mult = -ICE_SLOW)
}
pub fn chain_slow() -> BuffV1 {
    timed(E_CHAIN, CHAIN_SLOW_T, |b| b.move_speed_mult = -CHAIN_SLOW)
}
pub fn vulnerable() -> BuffV1 {
    timed(E_VULN, VULN_T, |b| b.damaged_amplify = VULN_AMP)
}
pub fn escape_speed() -> BuffV1 {
    timed(E_ESCAPE, ESCAPE_MS_T, |b| b.move_speed_mult = ESCAPE_MS)
}
pub fn excited() -> BuffV1 {
    timed(E_EXCITED, EXCITED_T, |b| {
        b.attack_speed_mult = EXCITED_AS;
        b.move_speed_mult = EXCITED_MS;
    })
}
/// 最终形态：不用 `cc_immune`——英雄放技能时自己挂的施法动作也是控制，免疫了可能连技能都放不出来；用韧性。
pub fn final_form() -> BuffV1 {
    timed(E_FINAL, FINAL_T, |b| {
        b.attack_speed_mult = FINAL_AS;
        b.move_speed_mult = FINAL_MS;
        b.damaged_reduce = FINAL_REDUCE;
        b.toughness = FINAL_TENACITY;
    })
}
pub fn undying() -> BuffV1 {
    timed(E_UNDYING, UNDYING_T, |b| b.undying = true)
}
pub fn ward_speed() -> BuffV1 {
    timed(E_WARD, WARD_MS_T, |b| b.move_speed_mult = WARD_MS)
}
pub fn tank_stacks(n: u8) -> BuffV1 {
    let mut b = BuffV1::named(S_TANK);
    b.hp = TANK_HP * n as i32;
    b.defence = TANK_RES * n as i32;
    b.magic_resistance = TANK_RES * n as i32;
    b
}
/// 坦克引擎这么多层时体型是第几档（None：还没变大）。
pub fn tank_size(n: u8) -> Option<usize> {
    TANK_BIG.iter().rposition(|&at| n >= at)
}
pub fn evil_stacks(n: u16) -> BuffV1 {
    let mut b = BuffV1::named(S_EVIL);
    b.magic_power = EVIL_AP * n as i32;
    b
}

// ===================== 特效 =====================

/// 屏幕上画的一种特效（[`super::fx`] 里每种一段动画）。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Show {
    Burn,
    Frost,
    LightPop,
    Escape,
    Grow,
    Punch,
    Heavy,
    /// 飞弹：从 `at` 飞到 `to[0]`，`dur` tick
    Missile,
    MissilePop,
    /// 连锁闪电：`at` 是放的人，`to` 是依次打到的人
    Chain,
    Crack,
    Ether,
    Stone,
    Execute,
    Dawn,
    Excited,
    /// 守护者：`at` 是队友，`to[0]` 是自己
    Guard,
    Wisp,
    /// 激光的瞄准圈（`dur` tick 后轰下来）
    LaserMark,
    Laser,
    /// 彗星从天上落到 `at`（落地是动画的后半）
    Comet,
    FinalForm,
    /// 雪球：从 `at` 飞到 `to[0]`，`dur` tick
    Snowball,
    SnowBurst,
    Quantum,
    Undying,
    Immolate,
    /// 风刃：`at` 是放的人，`to` 是打到的人
    Typhoon,
    Ward,
}

/// 屏幕那一场的一次特效：模拟的哪个 tick、在哪（模拟坐标）。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Out {
    pub tick: usize,
    pub show: Show,
    pub at: (u64, u64),
    pub to: Vec<(u64, u64)>,
    pub dur: u16,
}

// ===================== 状态 =====================

/// 一个座位：哪个玩家、哪一队、哪一路（击杀记录按队伍 + 分路认人）。
#[derive(Clone, Copy, Debug)]
pub struct Who {
    pub player: usize,
    pub team: usize,
    pub lane: u8,
}

/// 一个座位这边记着的。换了实体（复活）就是新的一条命，带 `*` 的从头来。
#[derive(Clone, Debug, Default)]
struct Pp {
    ent: Option<usize>,
    alive: bool,
    // * 上一次看到的
    seen: Option<usize>,
    hp: usize,
    max: usize,
    shield: usize,
    pos: (u64, u64),
    targetable: bool,
    hurt: bool,
    /// 这一次掉到了哪几条线下面（[`LOW_35`] 这些位）
    crossed: u8,
    /// 身上的硬控（按种类的位）、这一次新挂上的
    cc: u16,
    cc_new: u16,
    // * 上一次的四个冷却、每个格子最后一次放出来的 tick
    cds: Option<(usize, [usize; 4])>,
    cast: [Option<usize>; 4],
    // * 以太武器：(哪次放的技能, 到哪个 tick)
    ether: Option<(usize, usize)>,
    /// 伤害统计上次读到的数和那个 tick（跟着玩家）
    deal: Option<(u64, usize)>,
    /// 本包替他打的伤害在这一次的统计里：这一次不算他打中
    quiet_at: Option<usize>,
    /// 每种效果下次能触发的 tick
    ready: [usize; EV_N],
    /// 点亮他们：命中了几次、上一次
    hits: u32,
    last_hit: Option<usize>,
    /// 叠的层数（跟着玩家）和上次挂在哪个实体上、挂的是几层
    tank: u8,
    evil: u16,
    applied: Option<(usize, u8, u16)>,
    /// (种类, 对哪个座位, 到这个 tick 前不再)：每个目标各算的间隔、特效间隔
    gates: Vec<(Ev, usize, usize)>,
}

const LOW_35: u8 = 1;
const LOW_40: u8 = 2;
const LOW_15: u8 = 4;
const LINES: [(u8, usize); 3] = [(LOW_35, ESCAPE_PCT), (LOW_40, DAWN_PCT), (LOW_15, UNDYING_PCT)];

/// 算「控住」的控制：击飞、眩晕、定身、嘲讽、恐惧、魅惑（施法动作、位移、沉默不算）。
const HARD: [CcKindV1; 6] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

#[derive(Clone, Debug)]
struct Burn {
    holder: usize,
    hent: usize,
    victim: usize,
    vent: usize,
    per: usize,
    left: u8,
    next: usize,
}

#[derive(Clone, Debug)]
struct Hot {
    seat: usize,
    ent: usize,
    per: usize,
    left: u8,
    next: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Kind {
    Missile,
    Laser,
    Comet,
    Snowball,
}

/// 还在路上的：飞弹、激光、彗星、雪球。`base` 是放出去那一刻算好的伤害（不含按目标最大生命的那部分）。
#[derive(Clone, Debug)]
struct Shot {
    kind: Kind,
    holder: usize,
    hent: usize,
    team: usize,
    target: Option<(usize, usize)>,
    at: (u64, u64),
    land: usize,
    base: usize,
}

/// 一次看到的样子（这一步里不变的那份，效果照它算）。
#[derive(Clone, Copy, Debug, Default)]
struct L {
    ent: usize,
    alive: bool,
    team: usize,
    hp: usize,
    max: usize,
    pos: (u64, u64),
    targetable: bool,
    hurt: bool,
    crossed: u8,
    cc_new: u16,
}

/// 一份模拟的触发类海克斯。
#[derive(Clone, Debug, Default)]
pub struct Procs {
    pls: Vec<Pp>,
    burns: Vec<Burn>,
    hots: Vec<Hot>,
    shots: Vec<Shot>,
    kills_seen: usize,
    /// 本包给的控制（雪球的击飞）：(实体, 到这个 tick)，这期间他新挂上的控制不算谁控住的
    own_cc: Vec<(usize, usize)>,
    /// 每种触发了几次（END 一行）
    pub count: [u32; EV_N],
    /// 屏幕那一场这一步要画的（lib.rs 拿走放进 feed）
    pub out: Vec<Out>,
    /// 这一步的日志（lib.rs 拿走）
    pub log: Vec<String>,
    lines: usize,
}

fn d2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let (dx, dy) = (a.0.abs_diff(b.0), a.1.abs_diff(b.1));
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

fn within(a: (u64, u64), b: (u64, u64), r: u64) -> bool {
    d2(a, b) <= r.saturating_mul(r)
}

fn below(hp: usize, max: usize, pct: usize) -> bool {
    max > 0 && hp * 100 < max * pct
}

/// 统计里的一个数（`12`、`12.0`）。
pub fn parse_num(s: &str) -> Option<u64> {
    let t = s.trim();
    t.parse::<u64>().ok().or_else(|| t.parse::<f64>().ok().filter(|v| v.is_finite() && *v >= 0.0).map(|v| v as u64))
}

fn ad_ap(sim: &StableSim<'_>, ent: usize) -> (usize, usize) {
    sim.get_entity(ent).map_or((0, 0), |e| {
        let s = e.stat();
        (s.attack, s.magic_power)
    })
}

/// 挂一个限时 buff，已经有同名的就刷新时间（不叠）。
fn put_timed(sim: &mut StableSim<'_>, ent: usize, b: &BuffV1) {
    if sim.entity_stack_buff(ent, b, 1, true) == 0 {
        sim.entity_remove_buff(ent, b.name());
        sim.add_buff(ent, b);
    }
}

/// 这些种类里他有没有。
pub fn holds(set: u64, evs: &[Ev]) -> bool {
    evs.iter().any(|e| set & e.bit() != 0)
}

const ON_HIT: [Ev; 10] = [Ev::Firebrand, Ev::IceCold, Ev::LightEmUp, Ev::HeavyHitter, Ev::ChainLightning,
                          Ev::Vulnerability, Ev::EtherealWeapon, Ev::Executioner, Ev::PhenomenalEvil, Ev::Typhoon];
const ON_CC: [Ev; 2] = [Ev::Colossus, Ev::Cruelty];

/// 一份模拟里用到了哪些（`held` 每个座位一个位集）。
fn union(held: &[u64]) -> u64 {
    held.iter().fold(0, |a, h| a | h)
}

impl Procs {
    fn say(&mut self, screen: bool, f: impl FnOnce() -> String) {
        self.lines += 1;
        let n = self.lines;
        let keep = if screen { n <= 80 || n.is_multiple_of(40) } else { super::counted("proc").is_some() };
        if keep {
            self.log.push(format!("{} (proc line {n} of this match)", f()));
        }
    }

    fn show(&mut self, screen: bool, now: usize, show: Show, at: (u64, u64), to: Vec<(u64, u64)>, dur: usize) {
        if screen {
            self.out.push(Out { tick: now, show, at, to, dur: dur.min(u16::MAX as usize) as u16 });
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn hit(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, hent: usize, vent: usize, amount: usize,
           ty: DamageTypeV1, at: AttackTypeV1) {
        if amount == 0 {
            return;
        }
        sim.deal_damage_typed(hent, vent, amount, ty, at);
        self.pls[h].quiet_at = Some(now + EVERY);
    }

    /// 每个目标各自的间隔：到了返回 true 并记下一次。
    fn gate(&mut self, h: usize, ev: Ev, v: usize, now: usize, every: usize) -> bool {
        let g = &mut self.pls[h].gates;
        g.retain(|x| x.2 > now);
        if g.iter().any(|x| x.0 == ev && x.1 == v) {
            return false;
        }
        g.push((ev, v, now + every));
        true
    }

    fn fire(&mut self, ev: Ev) {
        self.count[ev as usize] += 1;
    }

    /// 叠层的 buff 现在挂着几层（复活了、层数变了：重挂）。
    fn keep_stacks(&mut self, sim: &mut StableSim<'_>, looks: &[L]) {
        for (i, look) in looks.iter().enumerate().take(self.pls.len()) {
            let (tank, evil) = (self.pls[i].tank, self.pls[i].evil);
            if (tank == 0 && evil == 0) || !look.alive {
                continue;
            }
            let ent = look.ent;
            if self.pls[i].applied == Some((ent, tank, evil)) {
                continue;
            }
            if tank > 0 {
                sim.entity_remove_buff(ent, S_TANK);
                sim.add_buff(ent, &tank_stacks(tank));
                for g in G_TANK {
                    sim.entity_remove_buff(ent, g);
                }
                if let Some(k) = tank_size(tank) {
                    sim.add_buff(ent, &BuffV1::named(G_TANK[k]));
                }
            }
            if evil > 0 {
                sim.entity_remove_buff(ent, S_EVIL);
                sim.add_buff(ent, &evil_stacks(evil));
            }
            self.pls[i].applied = Some((ent, tank, evil));
        }
    }

    /// 每个座位这一次的样子：生命、护盾、位置，掉没掉血、掉没掉到线下、新挂上的控制。
    fn look(&mut self, sim: &StableSim<'_>, now: usize, who: &[Who], any: u64) -> Vec<L> {
        let want_cc = holds(any, &ON_CC);
        self.own_cc.retain(|x| x.1 > now);
        let mut looks = vec![L::default(); who.len()];
        for (i, w) in who.iter().enumerate() {
            let p = &mut self.pls[i];
            let Some(e) = sim.get_player(w.player).and_then(|pl| pl.champion()) else {
                p.alive = false;
                p.seen = None;
                continue;
            };
            let ent = e.id();
            if p.ent != Some(ent) {
                // 新的一条命
                p.ent = Some(ent);
                p.seen = None;
                p.cds = None;
                p.cast = [None; 4];
                p.ether = None;
                p.cc = 0;
            }
            if !e.is_alive() {
                p.alive = false;
                p.seen = None;
                continue;
            }
            let ((hp, max), shield, pos) = (e.hp(), e.shield(), e.pos());
            let same = p.seen.and_then(|t| t.checked_add(EVERY)) == Some(now);
            p.hurt = same && hp + shield < p.hp + p.shield;
            p.crossed = 0;
            if same {
                for (bit, pct) in LINES {
                    if below(hp, max, pct) && !below(p.hp, p.max, pct) {
                        p.crossed |= bit;
                    }
                }
            }
            if want_cc {
                let mut cc = 0u16;
                for k in 0..e.cc_count() {
                    if let Some(c) = e.cc_at(k) {
                        if HARD.iter().any(|h| h.code() == c.kind) {
                            cc |= 1 << c.kind.min(15);
                        }
                    }
                }
                let ours = self.own_cc.iter().any(|x| x.0 == ent);
                p.cc_new = if same && !ours { cc & !p.cc } else { 0 };
                p.cc = cc;
            } else {
                p.cc_new = 0;
            }
            (p.hp, p.max, p.shield, p.pos, p.alive, p.seen, p.targetable) =
                (hp, max, shield, pos, true, Some(now), e.is_targetable());
            looks[i] = L { ent, alive: true, team: w.team, hp, max, pos, targetable: p.targetable, hurt: p.hurt,
                           crossed: p.crossed, cc_new: p.cc_new };
        }
        looks
    }

    /// 四个冷却一下子涨上去：放了（普攻、技能、技能 2、大招）。
    fn read_casts(&mut self, sim: &StableSim<'_>, now: usize, who: &[Who], held: &[u64], looks: &[L]) {
        for i in 0..who.len() {
            if held[i] == 0 || !looks[i].alive {
                continue;
            }
            let Some(c) = sim.get_player(who[i].player).and_then(|p| p.cooldowns()) else { continue };
            let c = [c.0, c.1, c.2, c.3];
            let p = &mut self.pls[i];
            if let Some((at, prev)) = p.cds {
                if at + EVERY == now {
                    for k in 0..4 {
                        if c[k] > prev[k] + JUMP[k] {
                            p.cast[k] = Some(now);
                        }
                    }
                }
            }
            p.cds = Some((now, c));
        }
    }

    /// 他这一次打中英雄没有：伤害统计涨了（上一次也读过，不是本包替他打的那一次）；读不到统计就看他刚出没出手。
    fn dealt(&mut self, sim: &StableSim<'_>, h: usize, player: usize, now: usize) -> bool {
        let v = sim.get_player(player).and_then(|p| p.statistics_json("deal")).as_deref().and_then(parse_num);
        let p = &mut self.pls[h];
        let quiet = p.quiet_at == Some(now);
        match v {
            Some(v) => {
                let before = p.deal;
                p.deal = Some((v, now));
                !quiet && matches!(before, Some((b, at)) if at.checked_add(EVERY) == Some(now) && v > b)
            }
            None => !quiet && p.cast.iter().flatten().any(|&t| now <= t + ACTION_WINDOW),
        }
    }

    pub fn step(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], held: &[u64], names: &[String],
                screen: bool) {
        let any = union(held);
        if any == 0 || who.is_empty() || held.len() != who.len() {
            return;
        }
        if self.pls.len() != who.len() {
            self.pls = vec![Pp::default(); who.len()];
        }
        let looks = self.look(sim, now, who, any);
        self.takedowns(sim, now, who, held, &looks, names, screen);
        self.read_casts(sim, now, who, held, &looks);
        for h in 0..who.len() {
            if held[h] == 0 || !looks[h].alive {
                continue;
            }
            if holds(held[h], &ON_HIT) {
                self.on_hit(sim, now, h, who, held[h], &looks, names, screen);
            }
            self.on_low(sim, now, h, held[h], &looks, names, screen);
            if holds(held[h], &ON_CC) {
                self.on_cc(sim, now, h, held[h], &looks, names, screen);
            }
            self.on_cast(sim, now, h, held[h], &looks, names, screen);
            self.timers(sim, now, h, held[h], &looks, names, screen);
        }
        self.burns_tick(sim, now, &looks, screen);
        self.hots_tick(sim, now, &looks);
        self.shots_tick(sim, now, &looks, names, screen);
        self.keep_stacks(sim, &looks);
    }

    // ---------- 参与击杀 ----------

    #[allow(clippy::too_many_arguments)]
    fn takedowns(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], held: &[u64], looks: &[L], names: &[String],
                 screen: bool) {
        let n = sim.kill_log_count();
        while self.kills_seen < n {
            let Some(k) = sim.kill_log_at(self.kills_seen) else { break };
            self.kills_seen += 1;
            let seat = |lane: u32| who.iter().position(|w| w.team == k.killer_team && w.lane as u32 == lane);
            let mut takers: Vec<usize> = seat(k.killer_position).into_iter().collect();
            for &a in &k.assist_positions[..(k.assist_count as usize).min(4)] {
                if let Some(s) = seat(a) {
                    if !takers.contains(&s) {
                        takers.push(s);
                    }
                }
            }
            for s in takers {
                if held[s] & Ev::TankEngine.bit() != 0 && self.pls[s].tank < TANK_MOST {
                    self.pls[s].tank += 1;
                    self.fire(Ev::TankEngine);
                    let t = self.pls[s].tank;
                    self.say(screen, || format!("PROC tank_engine {}: takedown - {t} stacks (+{} max health)", names[s],
                                                TANK_HP * t as i32));
                    if looks[s].alive {
                        self.show(screen, now, Show::Grow, looks[s].pos, Vec::new(), 0);
                    }
                }
                if held[s] & Ev::GetExcited.bit() != 0 && looks[s].alive {
                    put_timed(sim, looks[s].ent, &excited());
                    self.fire(Ev::GetExcited);
                    self.say(screen, || format!("PROC get_excited {}: takedown - +{EXCITED_AS}% attack speed for 5 s",
                                                names[s]));
                    self.show(screen, now, Show::Excited, looks[s].pos, Vec::new(), 0);
                }
            }
        }
    }

    // ---------- 打中英雄 ----------

    #[allow(clippy::too_many_arguments)]
    fn on_hit(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, who: &[Who], set: u64, looks: &[L],
              names: &[String], screen: bool) {
        let me = looks[h];
        let mut near: Vec<(u64, usize)> = (0..looks.len())
            .filter(|&v| looks[v].alive && looks[v].team != me.team)
            .map(|v| (d2(me.pos, looks[v].pos), v))
            .filter(|&(d, _)| d <= REACH * REACH)
            .collect();
        if near.is_empty() {
            // 身边没有敌方英雄：统计不读，上次的作废（下次靠近时重新读）
            let p = &mut self.pls[h];
            p.deal = p.deal.map(|(v, _)| (v, usize::MAX));
            return;
        }
        if !self.dealt(sim, h, who[h].player, now) {
            return;
        }
        near.retain(|&(_, v)| looks[v].hurt);
        if near.is_empty() {
            return;
        }
        near.sort();
        let victims: Vec<usize> = near.iter().take(VICTIMS).map(|x| x.1).collect();
        let first = victims[0];
        let (ad, ap) = ad_ap(sim, me.ent);
        if set & Ev::Firebrand.bit() != 0 {
            for &v in &victims {
                let per = (firebrand_total(looks[v].max, ad, ap) / FIREBRAND_PULSES as usize).max(1);
                match self.burns.iter_mut().find(|b| b.holder == h && b.vent == looks[v].ent) {
                    Some(b) => {
                        b.per = per;
                        b.left = FIREBRAND_PULSES;
                    }
                    None => {
                        self.burns.push(Burn { holder: h, hent: me.ent, victim: v, vent: looks[v].ent, per,
                                               left: FIREBRAND_PULSES, next: now });
                        self.fire(Ev::Firebrand);
                        self.say(screen, || format!("PROC firebrand {} ignites {}: {per} x {FIREBRAND_PULSES}", names[h],
                                                    names[v]));
                    }
                }
            }
        }
        if set & Ev::IceCold.bit() != 0 {
            for &v in &victims {
                put_timed(sim, looks[v].ent, &ice_slow());
                if self.gate(h, Ev::IceCold, v, now, ICE_T) {
                    self.fire(Ev::IceCold);
                    self.show(screen, now, Show::Frost, looks[v].pos, Vec::new(), 0);
                }
            }
        }
        if set & Ev::Vulnerability.bit() != 0 {
            for &v in &victims {
                put_timed(sim, looks[v].ent, &vulnerable());
                if self.gate(h, Ev::Vulnerability, v, now, VULN_T) {
                    self.fire(Ev::Vulnerability);
                    self.show(screen, now, Show::Crack, looks[v].pos, Vec::new(), 0);
                }
            }
        }
        if set & Ev::LightEmUp.bit() != 0 && self.pls[h].last_hit.is_none_or(|t| now >= t + LIGHT_GAP) {
            self.pls[h].last_hit = Some(now);
            self.pls[h].hits += 1;
            if self.pls[h].hits.is_multiple_of(LIGHT_EVERY) {
                let amount = light_damage(ad);
                self.hit(sim, now, h, me.ent, looks[first].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                self.fire(Ev::LightEmUp);
                self.say(screen, || format!("PROC light_em_up {} -> {}: {amount} physical", names[h], names[first]));
                self.show(screen, now, Show::LightPop, looks[first].pos, Vec::new(), 0);
            }
        }
        if set & Ev::HeavyHitter.bit() != 0 && self.gate(h, Ev::HeavyHitter, first, now, HEAVY_GAP) {
            let amount = me.max * HEAVY_PCT / 100;
            self.hit(sim, now, h, me.ent, looks[first].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
            self.fire(Ev::HeavyHitter);
            self.show(screen, now, Show::Heavy, looks[first].pos, Vec::new(), 0);
        }
        if set & Ev::EtherealWeapon.bit() != 0 {
            if let Some((cast, until)) = self.pls[h].ether {
                if now > cast && now <= until {
                    self.pls[h].ether = None;
                    let amount = ether_damage(ap, ad);
                    self.hit(sim, now, h, me.ent, looks[first].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    self.fire(Ev::EtherealWeapon);
                    self.say(screen, || format!("PROC ethereal_weapon {} -> {}: {amount} magic", names[h], names[first]));
                    self.show(screen, now, Show::Ether, looks[first].pos, Vec::new(), 0);
                }
            }
        }
        if set & Ev::Executioner.bit() != 0 {
            for &v in &victims {
                if below(looks[v].hp, looks[v].max, EXEC_PCT) && self.gate(h, Ev::Executioner, v, now, EXEC_GAP) {
                    let amount = looks[v].max * EXEC_DMG_PCT / 100;
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    self.fire(Ev::Executioner);
                    self.show(screen, now, Show::Execute, looks[v].pos, Vec::new(), 0);
                }
            }
        }
        if set & Ev::PhenomenalEvil.bit() != 0 && now >= self.pls[h].ready[Ev::PhenomenalEvil as usize]
            && self.pls[h].evil < EVIL_MOST {
            self.pls[h].ready[Ev::PhenomenalEvil as usize] = now + EVIL_GAP;
            self.pls[h].evil += 1;
            self.fire(Ev::PhenomenalEvil);
            self.show(screen, now, Show::Wisp, me.pos, Vec::new(), 0);
        }
        if set & Ev::ChainLightning.bit() != 0 && now >= self.pls[h].ready[Ev::ChainLightning as usize] {
            self.pls[h].ready[Ev::ChainLightning as usize] = now + CHAIN_CD;
            let mut others: Vec<(u64, usize)> = (0..looks.len())
                .filter(|&x| x != first && looks[x].alive && looks[x].team != me.team)
                .map(|x| (d2(looks[x].pos, looks[first].pos), x))
                .filter(|&(d, _)| d <= CHAIN_R * CHAIN_R)
                .collect();
            others.sort();
            let chain: Vec<usize> =
                std::iter::once(first).chain(others.into_iter().map(|o| o.1)).take(CHAIN_TARGETS).collect();
            let amount = chain_damage(ad, ap);
            for &x in &chain {
                self.hit(sim, now, h, me.ent, looks[x].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                put_timed(sim, looks[x].ent, &chain_slow());
            }
            self.fire(Ev::ChainLightning);
            self.say(screen, || {
                let hit: Vec<&str> = chain.iter().map(|&x| names[x].as_str()).collect();
                format!("PROC chain_lightning {}: {amount} magic to [{}]", names[h], hit.join(", "))
            });
            self.show(screen, now, Show::Chain, me.pos, chain.iter().map(|&x| looks[x].pos).collect(), 0);
        }
        if set & Ev::Typhoon.bit() != 0 && now >= self.pls[h].ready[Ev::Typhoon as usize] {
            let mut others: Vec<(u64, usize)> = (0..looks.len())
                .filter(|&x| x != first && looks[x].alive && looks[x].team != me.team && looks[x].targetable)
                .map(|x| (d2(looks[x].pos, me.pos), x))
                .filter(|&(d, _)| d <= TYPHOON_R * TYPHOON_R)
                .collect();
            if !others.is_empty() {
                others.sort();
                self.pls[h].ready[Ev::Typhoon as usize] = now + TYPHOON_CD;
                let amount = typhoon_damage(ad, ap).max(1);
                let blades: Vec<usize> = others.iter().take(TYPHOON_TARGETS).map(|o| o.1).collect();
                for &x in &blades {
                    self.hit(sim, now, h, me.ent, looks[x].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                }
                self.fire(Ev::Typhoon);
                self.show(screen, now, Show::Typhoon, me.pos, blades.iter().map(|&x| looks[x].pos).collect(), 0);
            }
        }
    }

    // ---------- 残血 ----------

    #[allow(clippy::too_many_arguments)]
    fn on_low(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, set: u64, looks: &[L], names: &[String],
              screen: bool) {
        let me = looks[h];
        let ready = |s: &Self, ev: Ev| now >= s.pls[h].ready[ev as usize];
        if set & Ev::EscapePlan.bit() != 0 && me.crossed & LOW_35 != 0 && ready(self, Ev::EscapePlan) {
            self.pls[h].ready[Ev::EscapePlan as usize] = now + ESCAPE_CD;
            let amount = escape_shield(me.max);
            sim.entity_add_shield(me.ent, amount, ESCAPE_SHIELD_T);
            put_timed(sim, me.ent, &escape_speed());
            self.fire(Ev::EscapePlan);
            self.say(screen, || format!("PROC escape_plan {}: below {ESCAPE_PCT}% ({}/{}) - shield {amount}", names[h],
                                        me.hp, me.max));
            self.show(screen, now, Show::Escape, me.pos, Vec::new(), 0);
        }
        if set & Ev::Dawnbringer.bit() != 0 && me.crossed & LOW_40 != 0 && ready(self, Ev::Dawnbringer) {
            self.pls[h].ready[Ev::Dawnbringer as usize] = now + DAWN_CD;
            let total = me.max.saturating_sub(me.hp) * DAWN_HEAL_PCT / 100;
            let per = (total / DAWN_PULSES as usize).max(1);
            self.hots.push(Hot { seat: h, ent: me.ent, per, left: DAWN_PULSES, next: now });
            self.fire(Ev::Dawnbringer);
            self.say(screen, || format!("PROC dawnbringers_resolve {}: below {DAWN_PCT}% - heal {total} over 2 s", names[h]));
            self.show(screen, now, Show::Dawn, me.pos, Vec::new(), 0);
        }
        if set & Ev::UndyingWill.bit() != 0 && me.crossed & LOW_15 != 0 && ready(self, Ev::UndyingWill) {
            self.pls[h].ready[Ev::UndyingWill as usize] = now + UNDYING_CD;
            put_timed(sim, me.ent, &undying());
            let per = (me.max * UNDYING_HEAL_PCT / 100 / UNDYING_PULSES as usize).max(1);
            self.hots.push(Hot { seat: h, ent: me.ent, per, left: UNDYING_PULSES, next: now });
            self.fire(Ev::UndyingWill);
            self.say(screen, || format!("PROC undying_will {}: below {UNDYING_PCT}% ({}/{}) - cannot die for 2 s",
                                        names[h], me.hp, me.max));
            self.show(screen, now, Show::Undying, me.pos, Vec::new(), 0);
        }
        if set & Ev::Guardian.bit() != 0 && ready(self, Ev::Guardian) {
            let ally = (0..looks.len()).find(|&a| {
                a != h && looks[a].alive && looks[a].team == me.team && looks[a].crossed & LOW_40 != 0
                    && within(looks[a].pos, me.pos, GUARD_R)
            });
            if let Some(a) = ally {
                self.pls[h].ready[Ev::Guardian as usize] = now + GUARD_CD;
                let amount = guard_shield(me.max);
                sim.entity_add_shield(looks[a].ent, amount, GUARD_T);
                sim.entity_add_shield(me.ent, amount, GUARD_T);
                self.fire(Ev::Guardian);
                self.say(screen, || format!("PROC guardian {} guards {}: shields of {amount}", names[h], names[a]));
                self.show(screen, now, Show::Guard, looks[a].pos, vec![me.pos], 0);
            }
        }
    }

    // ---------- 控住敌人 ----------

    #[allow(clippy::too_many_arguments)]
    fn on_cc(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, set: u64, looks: &[L], names: &[String],
             screen: bool) {
        let me = looks[h];
        let cast = self.pls[h].cast[1..].iter().flatten().any(|&t| now <= t + CC_WINDOW);
        if !cast {
            return;
        }
        let Some(v) = (0..looks.len()).find(|&v| {
            looks[v].alive && looks[v].team != me.team && looks[v].cc_new != 0 && within(looks[v].pos, me.pos, CC_REACH)
        }) else {
            return;
        };
        if set & Ev::Colossus.bit() != 0 && now >= self.pls[h].ready[Ev::Colossus as usize] {
            self.pls[h].ready[Ev::Colossus as usize] = now + COLOSSUS_CD;
            let amount = colossus_shield(me.max);
            sim.entity_add_shield(me.ent, amount, COLOSSUS_T);
            self.fire(Ev::Colossus);
            self.say(screen, || format!("PROC courage_of_the_colossus {} immobilized {}: shield {amount}", names[h],
                                        names[v]));
            self.show(screen, now, Show::Stone, me.pos, Vec::new(), 0);
        }
        if set & Ev::Cruelty.bit() != 0 && now >= self.pls[h].ready[Ev::Cruelty as usize] {
            self.pls[h].ready[Ev::Cruelty as usize] = now + COMET_CD;
            let (ad, ap) = ad_ap(sim, me.ent);
            self.shots.push(Shot { kind: Kind::Comet, holder: h, hent: me.ent, team: me.team, target: None,
                                   at: looks[v].pos, land: now + COMET_DELAY, base: comet_base(ap, ad) });
            self.fire(Ev::Cruelty);
            self.say(screen, || format!("PROC cruelty {} immobilized {}: a comet in 0.5 s", names[h], names[v]));
            self.show(screen, now, Show::Comet, looks[v].pos, Vec::new(), COMET_DELAY);
        }
    }

    // ---------- 放技能 / 普攻 ----------

    #[allow(clippy::too_many_arguments)]
    fn on_cast(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, set: u64, looks: &[L], names: &[String],
               screen: bool) {
        let me = looks[h];
        let cast = self.pls[h].cast;
        let at_now = |k: usize| cast[k] == Some(now);
        if set & Ev::MysticPunch.bit() != 0 && at_now(0) {
            sim.entity_reduce_cooldown(me.ent, SkillSlotV1::Skill, PUNCH_TICKS);
            sim.entity_reduce_cooldown(me.ent, SkillSlotV1::Skill2, PUNCH_TICKS);
            self.fire(Ev::MysticPunch);
            if self.gate(h, Ev::MysticPunch, h, now, 60) {
                self.show(screen, now, Show::Punch, me.pos, Vec::new(), 0);
            }
        }
        if set & Ev::EtherealWeapon.bit() != 0 && (1..4).any(at_now) {
            self.pls[h].ether = Some((now, now + ETHER_T));
        }
        if set & Ev::MagicMissile.bit() != 0 && (at_now(1) || at_now(2))
            && now >= self.pls[h].ready[Ev::MagicMissile as usize] {
            if let Some((d, v)) = nearest(looks, h, MISSILE_RANGE) {
                self.pls[h].ready[Ev::MagicMissile as usize] = now + MISSILE_CD;
                let t = ((d as f64).sqrt() as u64 / MISSILE_SPEED) as usize;
                let t = t.max(MISSILE_MIN_T);
                let (ad, ap) = ad_ap(sim, me.ent);
                self.shots.push(Shot { kind: Kind::Missile, holder: h, hent: me.ent, team: me.team,
                                       target: Some((v, looks[v].ent)), at: looks[v].pos, land: now + t,
                                       base: missile_damage(ap, ad) });
                self.fire(Ev::MagicMissile);
                self.show(screen, now, Show::Missile, me.pos, vec![looks[v].pos], t);
            }
        }
        if set & Ev::FinalForm.bit() != 0 && at_now(3) {
            put_timed(sim, me.ent, &final_form());
            self.fire(Ev::FinalForm);
            self.say(screen, || format!("PROC final_form {}: ultimate cast - 5 s of the final form", names[h]));
            self.show(screen, now, Show::FinalForm, me.pos, Vec::new(), 0);
        }
    }

    // ---------- 定时 ----------

    #[allow(clippy::too_many_arguments)]
    fn timers(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, set: u64, looks: &[L], names: &[String],
              screen: bool) {
        let me = looks[h];
        let ready = |s: &Self, ev: Ev| now >= s.pls[h].ready[ev as usize];
        if set & Ev::OrbitalLaser.bit() != 0 && ready(self, Ev::OrbitalLaser) {
            if let Some((_, v)) = nearest(looks, h, LASER_RANGE) {
                self.pls[h].ready[Ev::OrbitalLaser as usize] = now + LASER_CD;
                let (ad, ap) = ad_ap(sim, me.ent);
                self.shots.push(Shot { kind: Kind::Laser, holder: h, hent: me.ent, team: me.team, target: None,
                                       at: looks[v].pos, land: now + LASER_DELAY, base: laser_base(ap, ad) });
                self.say(screen, || format!("PROC orbital_laser {} marks {}", names[h], names[v]));
                self.show(screen, now, Show::LaserMark, looks[v].pos, Vec::new(), LASER_DELAY);
            }
        }
        if set & Ev::Snowball.bit() != 0 && ready(self, Ev::Snowball) {
            if let Some((_, v)) = nearest(looks, h, SNOW_RANGE) {
                self.pls[h].ready[Ev::Snowball as usize] = now + SNOW_CD;
                let (ad, ap) = ad_ap(sim, me.ent);
                self.shots.push(Shot { kind: Kind::Snowball, holder: h, hent: me.ent, team: me.team, target: None,
                                       at: looks[v].pos, land: now + SNOW_T, base: snow_base(ad, ap) });
                self.say(screen, || format!("PROC giant_snowball {} throws at {}", names[h], names[v]));
                self.show(screen, now, Show::Snowball, me.pos, vec![looks[v].pos], SNOW_T);
            }
        }
        if set & Ev::Quantum.bit() != 0 && ready(self, Ev::Quantum) {
            let hit: Vec<usize> = enemies_near(looks, h, me.pos, QUANTUM_R);
            if !hit.is_empty() {
                self.pls[h].ready[Ev::Quantum as usize] = now + QUANTUM_CD;
                let (ad, _) = ad_ap(sim, me.ent);
                for &v in &hit {
                    let amount = quantum_base(ad) + looks[v].max * QUANTUM_HP_PCT / 100;
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                }
                let heal = me.max * QUANTUM_HEAL_PCT / 100 * hit.len();
                sim.heal(me.ent, me.ent, heal);
                self.fire(Ev::Quantum);
                self.say(screen, || format!("PROC quantum_computing {}: {} champions slashed, healed {heal}", names[h],
                                            hit.len()));
                self.show(screen, now, Show::Quantum, me.pos, Vec::new(), 0);
            }
        }
        if set & Ev::Immolate.bit() != 0 && ready(self, Ev::Immolate) {
            self.pls[h].ready[Ev::Immolate as usize] = now + IMMOLATE_EVERY;
            let hit = enemies_near(looks, h, me.pos, IMMOLATE_R);
            if !hit.is_empty() {
                let amount = immolate_damage(me.max);
                for &v in &hit {
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Dot);
                }
                self.fire(Ev::Immolate);
                self.show(screen, now, Show::Immolate, me.pos, Vec::new(), 0);
            }
        }
        if set & Ev::SacredWard.bit() != 0 && ready(self, Ev::SacredWard) {
            let lowest = (0..looks.len())
                .filter(|&a| looks[a].alive && looks[a].team == me.team && within(looks[a].pos, me.pos, WARD_R)
                    && below(looks[a].hp, looks[a].max, WARD_BELOW_PCT))
                .min_by_key(|&a| (looks[a].hp * 1000 / looks[a].max.max(1), a));
            if let Some(a) = lowest {
                self.pls[h].ready[Ev::SacredWard as usize] = now + WARD_CD;
                let (_, ap) = ad_ap(sim, me.ent);
                let amount = ward_shield(ap, looks[a].max);
                sim.entity_add_shield(looks[a].ent, amount, WARD_T);
                put_timed(sim, looks[a].ent, &ward_speed());
                self.fire(Ev::SacredWard);
                self.say(screen, || format!("PROC sacred_ward {} wards {}: shield {amount}", names[h], names[a]));
                self.show(screen, now, Show::Ward, looks[a].pos, Vec::new(), 0);
            }
        }
    }

    // ---------- 持续的：点燃、回血、在路上的 ----------

    fn burns_tick(&mut self, sim: &mut StableSim<'_>, now: usize, looks: &[L], screen: bool) {
        let burns = std::mem::take(&mut self.burns);
        for mut b in burns {
            let on = |s: usize, e: usize| looks.get(s).is_some_and(|l| l.alive && l.ent == e);
            if !on(b.victim, b.vent) || !on(b.holder, b.hent) {
                continue;
            }
            if now >= b.next {
                self.hit(sim, now, b.holder, b.hent, b.vent, b.per, DamageTypeV1::Ap, AttackTypeV1::Dot);
                b.left -= 1;
                b.next = now + FIREBRAND_EVERY;
                self.show(screen, now, Show::Burn, looks[b.victim].pos, Vec::new(), 0);
            }
            if b.left > 0 {
                self.burns.push(b);
            }
        }
    }

    fn hots_tick(&mut self, sim: &mut StableSim<'_>, now: usize, looks: &[L]) {
        let hots = std::mem::take(&mut self.hots);
        for mut x in hots {
            if !looks.get(x.seat).is_some_and(|l| l.alive && l.ent == x.ent) {
                continue;
            }
            if now >= x.next {
                sim.heal(x.ent, x.ent, x.per);
                x.left -= 1;
                x.next = now + HOT_EVERY;
            }
            if x.left > 0 {
                self.hots.push(x);
            }
        }
    }

    fn shots_tick(&mut self, sim: &mut StableSim<'_>, now: usize, looks: &[L], names: &[String], screen: bool) {
        let shots = std::mem::take(&mut self.shots);
        for s in shots {
            if now < s.land {
                self.shots.push(s);
                continue;
            }
            // 放的人死了（或者换了身体）：这一发不算了
            if !looks.get(s.holder).is_some_and(|l| l.alive && l.ent == s.hent) {
                continue;
            }
            match s.kind {
                Kind::Missile => {
                    let Some((v, vent)) = s.target else { continue };
                    if !looks.get(v).is_some_and(|l| l.alive && l.ent == vent) {
                        continue;
                    }
                    self.hit(sim, now, s.holder, s.hent, vent, s.base, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    self.show(screen, now, Show::MissilePop, looks[v].pos, Vec::new(), 0);
                }
                Kind::Laser | Kind::Comet | Kind::Snowball => {
                    let (r, pct, ty) = match s.kind {
                        Kind::Laser => (LASER_R, LASER_HP_PCT, DamageTypeV1::Ap),
                        Kind::Comet => (COMET_R, COMET_HP_PCT, DamageTypeV1::Ap),
                        _ => (SNOW_R, SNOW_HP_PCT, DamageTypeV1::Ad),
                    };
                    let hit: Vec<usize> = (0..looks.len())
                        .filter(|&v| looks[v].alive && looks[v].team != s.team && within(looks[v].pos, s.at, r))
                        .collect();
                    for &v in &hit {
                        if s.kind == Kind::Snowball {
                            sim.apply_cc(looks[v].ent, &CcV1::of_kind(CcKindV1::Airborne, SNOW_AIR));
                            self.own_cc.push((looks[v].ent, now + EVERY * 2));
                        }
                        let amount = s.base + looks[v].max * pct / 100;
                        self.hit(sim, now, s.holder, s.hent, looks[v].ent, amount, ty, AttackTypeV1::Skill);
                    }
                    let (ev, what, show) = match s.kind {
                        Kind::Laser => (Ev::OrbitalLaser, "orbital_laser strikes", Some(Show::Laser)),
                        Kind::Comet => (Ev::Cruelty, "cruelty's comet lands", None),
                        _ => (Ev::Snowball, "giant_snowball lands", Some(Show::SnowBurst)),
                    };
                    self.fire(ev);
                    let n = hit.len();
                    let h = s.holder;
                    self.say(screen, || format!("PROC {what} for {}: {n} champions hit ({} + % max health)", names[h],
                                                s.base));
                    if let Some(show) = show {
                        self.show(screen, now, show, s.at, Vec::new(), 0);
                    }
                }
            }
        }
    }

    /// 每种触发了几次（不是 0 的）。
    pub fn summary(&self) -> String {
        let parts: Vec<String> = (1..EV_N)
            .filter(|&e| self.count[e] > 0)
            .filter_map(|e| {
                super::augments::AUGS.iter().find(|a| a.ev as usize == e).map(|a| format!("{} {}", a.key, self.count[e]))
            })
            .collect();
        if parts.is_empty() {
            "-".into()
        } else {
            parts.join(", ")
        }
    }

    /// 测试看的：这个座位叠了几层（坦克引擎、惊世邪恶）。
    #[cfg(test)]
    pub fn stacks(&self, seat: usize) -> (u8, u16) {
        self.pls.get(seat).map_or((0, 0), |p| (p.tank, p.evil))
    }
}

/// 离 `h` 最近的、选得中的敌方英雄（`r` 以内）：(距离的平方, 座位)。
fn nearest(looks: &[L], h: usize, r: u64) -> Option<(u64, usize)> {
    let me = looks[h];
    (0..looks.len())
        .filter(|&v| looks[v].alive && looks[v].team != me.team && looks[v].targetable)
        .map(|v| (d2(me.pos, looks[v].pos), v))
        .filter(|&(d, _)| d <= r * r)
        .min()
}

/// `at` 周围 `r` 以内 `h` 的敌方英雄。
fn enemies_near(looks: &[L], h: usize, at: (u64, u64), r: u64) -> Vec<usize> {
    let team = looks[h].team;
    (0..looks.len()).filter(|&v| looks[v].alive && looks[v].team != team && within(looks[v].pos, at, r)).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_numbers_follow_the_cards() {
        // a 2000-health target, 200 attack damage, 300 ability power
        assert_eq!(firebrand_total(2000, 200, 300), 30 + 60 + 20 + 30);
        assert_eq!(light_damage(200), 105);
        assert_eq!(escape_shield(2000), 340);
        assert_eq!(missile_damage(300, 200), 30 + 75 + 20);
        assert_eq!(chain_damage(200, 300), 40 + 50 + 90);
        assert_eq!(immolate_damage(4000), 75);
        assert_eq!(ward_shield(300, 2000), 100 + 75 + 160);
        assert_eq!(tank_size(5), None);
        assert_eq!(tank_size(6), Some(0));
        assert_eq!(tank_size(12), Some(1));
        let b = tank_stacks(12);
        assert_eq!((b.hp, b.defence, b.magic_resistance), (360, 36, 36));
        assert_eq!(evil_stacks(EVIL_MOST).magic_power, 150);
        let f = final_form();
        assert_eq!((f.attack_speed_mult, f.damaged_reduce, f.toughness, f.cc_immune), (30, 20, 80, false));
        assert!(undying().undying);
        assert_eq!(parse_num(" 12.0 "), Some(12));
        assert!(below(29, 100, 30) && !below(30, 100, 30) && !below(0, 0, 30));
    }

    #[test]
    fn every_buff_name_fits() {
        for n in [E_ICE, E_CHAIN, E_VULN, E_ESCAPE, E_EXCITED, E_FINAL, E_UNDYING, E_WARD, S_TANK, S_EVIL, G_TANK[0],
                  G_TANK[1]] {
            assert!(n.len() <= BUFF_NAME_CAP && n.starts_with("league_hextech_"), "{n}");
            assert!(super::super::augments::of_buff(n).is_none(), "{n} is no augment's marker");
        }
    }
}
