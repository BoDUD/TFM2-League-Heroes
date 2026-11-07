//! 保护射手（peel）：比赛 AI 改进的第一步，依据逆向出来的游戏 AI 结构（docs/native_ai.md）。
//!
//! 游戏自己的团战 AI（game-ai：big_plan/battle 的 FOCUS-SEL 选目标、sub_plan/battle 的 Peel 战术、support_target）
//! 让每个人各打各的：对面英雄贴到我方射手身上时，辅助常常还在打前排或小兵（用户 2026-11-08「坦克保护adc
//! 现在游戏里也很糟糕吧」）。这个钩子只改这一种情况：
//!
//! - 我方射手（Bottom）身边 `DIVE_R` 以内有看得见的敌方英雄 = 贴脸的人（离射手最近的那个）；
//! - 保镖：辅助（血量 ≥ `SUPPORT_HP`%），以及离射手 `GUARD_NEAR` 以内的上单、打野（血量 ≥ `GUARD_HP`%），
//!   离贴脸的人 `REACH` 以内才管；
//! - 游戏 AI 给保镖的普攻目标不是他 → 改打他；往前走（不是撤退，血量 ≥ `MOVE_HP`%）→ 改打他；对着别的敌方英雄放的
//!   指向技能 → 改指向他（游戏认这个指令才改）；没有指令 → 打他。撤退、回城、给自己 / 队友的技能、方向 / 位置技能、
//!   已经在打他的，都不动。
//!
//! 优先级 `PRIORITY` 在 league_macro（大龙后抱团 / 推基地）之后、英雄附加包之前：英雄的钩子（替 AI 放大招之类）还能在它
//! 之后改。只看比赛状态，没有随机数：服务器预演和客户端重演走的一样。每个选手自己的钩子实例，不共用状态。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_peel.log`（每次启动重写，上一次的留在 .prev.log）。
//! 只记服务器预演：射手每被贴脸一次（同一个保镖 `GAP` 内算一次）记下游戏 AI 原本让保镖做什么——这就是看游戏 AI 自己
//! 会不会保护射手；前 `DETAIL_LINES` 次各一行，每 `SUM_EVERY` 次一行汇总，汇总也追加到不随启动重写的 league_peel.sum.log。
//! 保护的效果看 league_fight_log 的 SUM 行（射手被贴脸后有没有人来、射手死了没有）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_peel";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时合集的 build.rs 给 ADDON_VERSION_<id>。
const VERSION: &str = match option_env!("ADDON_VERSION_league_peel") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：league_macro（-500_000）之后，英雄附加包（1_000_000 上下）之前。
pub const PRIORITY: i32 = -400_000;
/// 敌方英雄离我方射手多近算贴脸（和 league_fight_log 的 DIVE_R 一样）。
pub const DIVE_R: f64 = 30_000.0;
/// 上单、打野离射手多近才当保镖（辅助不管远近）。
pub const GUARD_NEAR: f64 = 60_000.0;
/// 保镖离贴脸的人多远以内才去打他。
pub const REACH: f64 = 80_000.0;
/// 辅助的血量下限（%）。
pub const SUPPORT_HP: usize = 25;
/// 上单、打野的血量下限（%）。
pub const GUARD_HP: usize = 40;
/// 游戏 AI 让保镖往前走时，血量到这么多（%）才改成去打贴脸的人。
pub const MOVE_HP: usize = 50;
/// 移动的终点比现在离贴脸的人远这么多 = 撤退，不动。
pub const RETREAT: f64 = 10_000.0;
/// 同一个保镖两次贴脸隔这么久（tick，2 秒）以上才算新的一次。
pub const GAP: usize = 120;
/// 地图外的坐标（死了、在泉水外面之类）不算。
pub const MAP_MAX: f64 = 1_200_000.0;
const TOP: u32 = 0;
const JUNGLE: u32 = 1;
const BOTTOM: u32 = 3;
const SUPPORT: u32 = 4;
/// 每这么多次贴脸写一行汇总。
pub const SUM_EVERY: usize = 500;
const DETAIL_LINES: usize = 60;
const LOG_CAP: usize = 5_000;

pub type Pos = (f64, f64);

pub fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn on_map(p: Pos) -> bool {
    (0.0..=MAP_MAX).contains(&p.0) && (0.0..=MAP_MAX).contains(&p.1)
}

// ===================== 决定 =====================

/// 贴脸开始时游戏 AI 原本让保镖做的事。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Native {
    Nothing = 0,
    AttackDiver = 1,
    AttackOther = 2,
    MoveIn = 3,
    MoveOut = 4,
    SkillDiver = 5,
    SkillOther = 6,
    Recall = 7,
}

pub const NATIVE: [&str; 8] =
    ["no order", "hit the diver", "hit something else", "walk in", "walk away", "skill on the diver", "skill elsewhere", "recall"];

/// 移动的终点比现在离贴脸的人远 `RETREAT` 以上。
pub fn retreat(me: Pos, to: Pos, diver: Pos) -> bool {
    dist(to, diver) > dist(me, diver) + RETREAT
}

fn on_target(b: &InputV1, id: usize) -> bool {
    b.target.kind == InputTargetKindV1::Target.code() && b.target.target_id == id
}

pub fn classify(base: Option<&InputV1>, diver: usize, diver_at: Pos, me: Pos) -> Native {
    let Some(b) = base else { return Native::Nothing };
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Attack) if on_target(b, diver) => Native::AttackDiver,
        Some(InputKindV1::Attack) => Native::AttackOther,
        Some(InputKindV1::Move) if retreat(me, (b.x as f64, b.y as f64), diver_at) => Native::MoveOut,
        Some(InputKindV1::Move) => Native::MoveIn,
        Some(InputKindV1::Return) => Native::Recall,
        Some(_) if on_target(b, diver) => Native::SkillDiver,
        Some(_) => Native::SkillOther,
        None => Native::Nothing,
    }
}

/// 这一 tick 场上和这个保镖有关的东西。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct View {
    pub me: Pos,
    pub hp_pct: usize,
    /// 自己的位置（LaneV1 代码）。
    pub lane: u32,
    /// 我方射手（活着、在地图上）。
    pub carry: Option<Pos>,
    /// 贴脸的人：离射手最近、`DIVE_R` 以内、看得见的敌方英雄。
    pub diver: Option<(usize, Pos)>,
    /// 看得见的敌方英雄。
    pub enemies: Vec<usize>,
}

/// 保镖这次要管就给出贴脸的人：位置对、血量够、够得着。
pub fn guarding(v: &View) -> Option<(usize, Pos)> {
    let carry = v.carry?;
    let diver = v.diver?;
    let floor = match v.lane {
        SUPPORT => SUPPORT_HP,
        TOP | JUNGLE if dist(v.me, carry) <= GUARD_NEAR => GUARD_HP,
        _ => return None,
    };
    (v.hp_pct >= floor && dist(v.me, diver.1) <= REACH).then_some(diver)
}

/// 这一 tick 的保护指令：`Some` 换掉游戏 AI 的指令，`None` 照旧。
pub fn order(v: &View, base: Option<&InputV1>, valid: &dyn Fn(&InputV1) -> bool) -> Option<InputV1> {
    let (diver, at) = guarding(v)?;
    let hit = InputV1::action(InputKindV1::Attack, InputTargetV1::target(diver));
    let out = match classify(base, diver, at, v.me) {
        Native::AttackDiver | Native::SkillDiver | Native::MoveOut | Native::Recall => return None,
        Native::Nothing | Native::AttackOther => hit,
        Native::MoveIn if v.hp_pct >= MOVE_HP => hit,
        Native::MoveIn => return None,
        Native::SkillOther => {
            let b = base?;
            // 只改对着别的敌方英雄放的指向技能：给自己、队友、小兵的和方向 / 位置技能都不动
            if b.target.kind != InputTargetKindV1::Target.code() || !v.enemies.contains(&b.target.target_id) {
                return None;
            }
            InputV1 { target: InputTargetV1::target(diver), ..*b }
        }
    };
    valid(&out).then_some(out)
}

fn look(sim: &StableSim<'_>, player: usize, team: usize) -> Option<View> {
    let me_p = sim.get_player(player)?;
    let champ = me_p.champion()?;
    if !champ.is_alive() {
        return None;
    }
    let (hp, max) = champ.hp();
    let (x, y) = champ.pos();
    let mut v = View {
        me: (x as f64, y as f64),
        hp_pct: if max > 0 { hp * 100 / max } else { 0 },
        lane: me_p.lane()?.code(),
        ..View::default()
    };
    let mut enemies: Vec<(usize, Pos)> = Vec::new();
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else { continue };
        let Some(c) = p.champion() else { continue };
        if !c.is_alive() {
            continue;
        }
        let (x, y) = c.pos();
        let at = (x as f64, y as f64);
        if !on_map(at) {
            continue;
        }
        if p.team() == team {
            if p.lane().map(|l| l.code()) == Some(BOTTOM) {
                v.carry = Some(at);
            }
        } else if sim.is_visible(team, c.id()) {
            enemies.push((c.id(), at));
        }
    }
    if let Some(carry) = v.carry {
        v.diver = enemies
            .iter()
            .filter(|(_, at)| dist(*at, carry) <= DIVE_R)
            .min_by(|a, b| dist(a.1, carry).total_cmp(&dist(b.1, carry)))
            .copied();
    }
    v.enemies = enemies.into_iter().map(|e| e.0).collect();
    Some(v)
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
static SUM_HEADER: AtomicBool = AtomicBool::new(false);
/// 服务器预演里的统计：贴脸次数按 [保镖位置][游戏 AI 原本的指令]，改过指令的 tick 按保镖位置。
static BOOK: Mutex<Book> = Mutex::new(Book { episodes: [[0; 8]; 5], changed: [0; 5], total: 0 });

struct Book {
    episodes: [[usize; 8]; 5],
    changed: [usize; 5],
    total: usize,
}

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_PEEL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_peel.log");
        }
    }
    PathBuf::from("league_peel.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    if LINES.fetch_add(1, Ordering::Relaxed) >= LOG_CAP {
        return;
    }
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// 汇总行也追加到 league_peel.sum.log（每次启动先写一行日期和版本）。
fn sum_log(line: &str) {
    let Ok(mut f) = OpenOptions::new().create(true).append(true).open(LOG_PATH.with_extension("sum.log")) else { return };
    let mut text = String::new();
    if !SUM_HEADER.swap(true, Ordering::Relaxed) {
        let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_or(0, |d| d.as_secs());
        let (y, m, d) = civil(secs / 86_400);
        text.push_str(&format!("=== {y}-{m:02}-{d:02} {:02}:{:02} UTC: {ID} v{VERSION} ===\n", secs / 3600 % 24, secs / 60 % 60));
    }
    text.push_str(line);
    text.push('\n');
    let _ = f.write_all(text.as_bytes());
}

/// 1970-01-01 起的天数 -> (年, 月, 日)。
pub fn civil(days: u64) -> (i64, u32, u32) {
    let z = days as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = (if mp < 10 { mp + 3 } else { mp - 9 }) as u32;
    (yoe + era * 400 + i64::from(m <= 2), m, d)
}

fn pct(n: usize, of: usize) -> String {
    if of == 0 {
        "-".to_string()
    } else {
        format!("{:.0}%", 100.0 * n as f64 / of as f64)
    }
}

fn lane_name(lane: u32) -> &'static str {
    ["top", "jungle", "mid", "bottom", "support"].get(lane as usize).copied().unwrap_or("?")
}

/// 汇总：游戏 AI 原本让保镖做什么（各位置），我们改了多少 tick。
pub fn sum_line(episodes: &[[usize; 8]; 5], changed: &[usize; 5], total: usize) -> String {
    let all: Vec<usize> = (0..8).map(|k| episodes.iter().map(|r| r[k]).sum()).collect();
    let n: usize = all.iter().sum();
    let whole = NATIVE.iter().zip(&all).map(|(name, c)| format!("{name} {}", pct(*c, n))).collect::<Vec<_>>().join(", ");
    let lanes = [SUPPORT, TOP, JUNGLE]
        .iter()
        .map(|&l| {
            let row = &episodes[l as usize];
            let m: usize = row.iter().sum();
            format!("{} {m} (on the diver {})", lane_name(l), pct(row[Native::AttackDiver as usize] + row[Native::SkillDiver as usize], m))
        })
        .collect::<Vec<_>>()
        .join(", ");
    format!(
        "SUM {total} dives (a guard in reach when an enemy came within {}k of our ADC): the game's AI had the guard {whole} | by guard: {lanes} | ticks we changed: support {}, top {}, jungle {}",
        DIVE_R / 1000.0,
        changed[SUPPORT as usize],
        changed[TOP as usize],
        changed[JUNGLE as usize]
    )
}

fn clock(tick: usize) -> String {
    let s = tick / 60;
    format!("{}:{:02}", s / 60, s % 60)
}

/// 服务器预演里一次新的贴脸：记下游戏 AI 原本的指令。
fn note_dive(lane: u32, native: Native, detail: impl FnOnce() -> String) {
    let (total, sum) = {
        let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        if let Some(row) = book.episodes.get_mut(lane as usize) {
            row[native as usize] += 1;
        }
        book.total += 1;
        let total = book.total;
        let sum = (total % SUM_EVERY == 0).then(|| sum_line(&book.episodes, &book.changed, total));
        (total, sum)
    };
    if total <= DETAIL_LINES {
        wlog(detail());
    }
    if let Some(line) = sum {
        wlog(&line);
        sum_log(&line);
    }
}

fn note_change(lane: u32) {
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(c) = book.changed.get_mut(lane as usize) {
        *c += 1;
    }
}

// ===================== 钩子 =====================

#[derive(Clone, Default)]
struct Peel {
    /// 上次看到要保护射手的 tick（新的一次贴脸 = 隔了 `GAP` 以上，或者比赛重开、tick 倒回去了）。
    last_dive: Option<usize>,
}

impl StablePlayerAi for Peel {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:peel")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // 中单、射手从不当保镖：不看场上
        if !matches!(ctx.lane().map(|l| l.code()), Some(TOP | JUNGLE | SUPPORT)) {
            return None;
        }
        let tick = ctx.tick();
        let (player, team) = (ctx.player_id(), ctx.team());
        let (v, presim) = {
            let sim = ctx.sim()?;
            let presim = sim
                .sim_origin()
                .is_some_and(|o| SimOriginKindV1::from_code(o.kind) == Some(SimOriginKindV1::ServerPresim));
            (look(&sim, player, team)?, presim)
        };
        let Some((diver, at)) = guarding(&v) else { return None };
        let fresh = self.last_dive.is_none_or(|t| tick < t || tick > t + GAP);
        self.last_dive = Some(tick);
        if fresh && presim {
            // the champion's name only for the log line, not every tick
            let head = ctx.sim().and_then(|s| s.get_player(player).and_then(|p| p.champion()).and_then(|c| c.name()));
            let native = classify(base.as_ref(), diver, at, v.me);
            note_dive(v.lane, native, || {
                format!(
                    "DIVE t={} {} ({}) T{team}: enemy #{diver} {:.0}k from our ADC, guard {:.0}k from it at {}% hp - the game's AI: {}",
                    clock(tick),
                    head.unwrap_or_default(),
                    lane_name(v.lane),
                    v.carry.map_or(0.0, |c| dist(c, at) / 1000.0),
                    dist(v.me, at) / 1000.0,
                    v.hp_pct,
                    NATIVE[native as usize]
                )
            });
        }
        let out = order(&v, base.as_ref(), &|i| ctx.is_valid_input(i))?;
        if presim {
            note_change(v.lane);
        }
        Some(out)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (peel: the support and nearby top / jungle hit whoever dives our ADC) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Peel::default());
    host.log(LogLevel::Info, "league_peel loaded (peel the ADC).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    const CARRY: Pos = (500_000.0, 700_000.0);
    const DIVER: usize = 77;

    fn view(lane: u32) -> View {
        View {
            me: (520_000.0, 700_000.0),
            hp_pct: 80,
            lane,
            carry: Some(CARRY),
            diver: Some((DIVER, (510_000.0, 690_000.0))),
            enemies: vec![DIVER, 78, 79],
        }
    }

    fn yes(_: &InputV1) -> bool {
        true
    }

    fn attack(id: usize) -> InputV1 {
        InputV1::action(InputKindV1::Attack, InputTargetV1::target(id))
    }

    #[test]
    fn the_support_hits_the_diver_instead() {
        let v = view(SUPPORT);
        for base in [Some(attack(78)), Some(attack(5_000)), None, Some(InputV1::move_to(505_000, 695_000))] {
            let out = order(&v, base.as_ref(), &yes).expect("peels");
            assert_eq!((out.kind, out.target.target_id), (InputKindV1::Attack.code(), DIVER));
        }
        // already on him, walking away, recalling: left alone
        assert_eq!(order(&v, Some(&attack(DIVER)), &yes), None);
        assert_eq!(order(&v, Some(&InputV1::move_to(700_000, 700_000)), &yes), None, "a retreat stays");
        assert_eq!(order(&v, Some(&InputV1::return_home()), &yes), None);
        // the game refuses the attack: keep its order
        assert_eq!(order(&v, Some(&attack(78)), &|_| false), None);
    }

    #[test]
    fn skills_on_other_champions_turn_on_the_diver() {
        let v = view(SUPPORT);
        let stun = InputV1::action(InputKindV1::Skill, InputTargetV1::target(78));
        let out = order(&v, Some(&stun), &yes).unwrap();
        assert_eq!((out.kind, out.target.target_id), (InputKindV1::Skill.code(), DIVER));
        // a heal on an ally, a skillshot by direction, a skill on a minion: left alone
        let heal = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(3));
        assert_eq!(order(&v, Some(&heal), &yes), None);
        let shot = InputV1::action(InputKindV1::Ult, InputTargetV1::dir(1, 0));
        assert_eq!(order(&v, Some(&shot), &yes), None);
        assert_eq!(order(&v, Some(&InputV1::action(InputKindV1::Skill, InputTargetV1::target(5_000))), &yes), None);
    }

    #[test]
    fn who_guards() {
        // top / jungle only near the ADC, mid and the ADC never
        assert!(guarding(&view(TOP)).is_some());
        assert!(guarding(&View { me: (585_000.0, 700_000.0), ..view(JUNGLE) }).is_none(), "85k from the ADC");
        assert!(guarding(&View { me: (585_000.0, 700_000.0), ..view(SUPPORT) }).is_some(), "the support comes from farther");
        assert!(guarding(&view(2)).is_none() && guarding(&view(BOTTOM)).is_none());
        // hp floors and reach
        assert!(guarding(&View { hp_pct: 30, ..view(SUPPORT) }).is_some());
        assert!(guarding(&View { hp_pct: 20, ..view(SUPPORT) }).is_none());
        assert!(guarding(&View { hp_pct: 35, ..view(TOP) }).is_none());
        assert!(guarding(&View { me: (600_000.0, 690_000.0), ..view(SUPPORT) }).is_none(), "90k from the diver");
        // no diver or no ADC: nothing
        assert!(guarding(&View { diver: None, ..view(SUPPORT) }).is_none());
        assert!(guarding(&View { carry: None, ..view(SUPPORT) }).is_none());
    }

    #[test]
    fn a_hurt_guard_does_not_walk_in() {
        let v = View { hp_pct: 45, ..view(SUPPORT) };
        assert_eq!(order(&v, Some(&InputV1::move_to(505_000, 695_000)), &yes), None);
        assert!(order(&v, Some(&attack(78)), &yes).is_some(), "but switches its attack");
    }

    #[test]
    fn the_summary_and_dates() {
        let mut e = [[0usize; 8]; 5];
        e[SUPPORT as usize][Native::AttackOther as usize] = 3;
        e[SUPPORT as usize][Native::AttackDiver as usize] = 1;
        e[TOP as usize][Native::MoveIn as usize] = 1;
        let line = sum_line(&e, &[2, 0, 0, 0, 7], 5);
        assert!(line.starts_with("SUM 5 dives"), "{line}");
        assert!(line.contains("hit the diver 20%") && line.contains("hit something else 60%"), "{line}");
        assert!(line.contains("support 4 (on the diver 25%)") && line.contains("top 1 (on the diver 0%)"), "{line}");
        assert!(line.ends_with("support 7, top 2, jungle 0"), "{line}");
        assert_eq!(civil(20_400), (2025, 11, 8));
        assert_eq!(classify(None, DIVER, CARRY, CARRY), Native::Nothing);
        assert_eq!(clock(3_660), "1:01");
    }
}
