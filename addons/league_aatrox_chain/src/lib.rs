//! 剑魔 W 锁链附加包 v0.2.3：W「恶火束链」照 League 原版。
//!
//! 主包的 W（数据）：锁链停在第一个敌人身上（伤害 + 减速 1.5 秒）；打中英雄时在落点放圈，1.5 秒后那个英雄
//! 再受一次伤害、被拉向剑魔。League 的两条数据写不出来：走出圈锁链就断、拉回的是圈的中心。
//! `mod.override_info` 把主包的剑魔换成 `override/` 里的副本：锁链打中的那一下调本包的 `chain`。
//!
//! 本包只做判断和位移，看得见的和伤害都留给数据层（v0.1 由本包自己播圈、打第二下，游戏里看不到：
//! 「w技能完全看不到效果」）。本包在剑魔身上挂几个短标记，副本里锁链的数据读标记再播画面、打伤害：
//!
//! - `chain`（锁链打中谁就对谁调，League：只有这一个人）：
//!   - 英雄或野怪（League：英雄和大型野怪；TFM2 的野怪都是单只的大怪）：锁住。圈心是锁链停下的地方
//!     （锁链碰到他就停，比他稍微靠近剑魔，League 也是这样），他身上挂
//!     `league_aatrox_chain_on:<圈心x>:<圈心y>:<剑魔>:<到点tick>`，然后每 tick 看着他（`watch`，以他为施法者
//!     排队，剑魔死了也照样跑）。剑魔身上挂 `w_tether`（数据在锁链落点播圈），打中的是英雄再挂 `w_champ`
//!     （数据给第一下记 E 的吸血、被动冷却、大灭击杀）。
//!   - 小兵：剑魔身上挂 `w_minion`，数据再打一下（League：对小兵双倍）。
//! - `watch`：走出画出来的圈（横向 `AREA`、上下 `AREA_Y` 的椭圆；走出去、闪现、冲刺都算）→ 锁链断，什么都不发生；到 `HOLD` tick（1.5 秒）
//!   还在圈里 → 拉回圈心（引擎的强制位移 ForceMove，撞墙会停），剑魔身上挂 `w_pull`（英雄再挂
//!   `w_pull_c`）：数据在 `READ_AT` tick 读到，打第二下（按剑魔当下的攻击力）、播缠身和收紧的画面，
//!   英雄再记吸血、被动、击杀。拴着的时候每 `LINK_EVERY` tick 从他脚下往圈心飞一节锁链
//!   （`league_aatrox_w_link`，贴着地面：两头都往下挪 `LINK_DROP`，和圈的画面一样落在脚下）。
//! - `drag`：拉回被韧性截短了就再推剩下的路，直到到圈心；比上次没近多少（撞墙、免控）就停。
//!
//! 只碰被剑魔 W 打中的单位；状态都在单位身上的 buff 和排队的效果里，不用全局变量，服务端预模拟和你看的
//! 那场各算各的。League 的「真实视野」（被锁住的人现形）没有接口，没做。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aatrox_chain.log`，每次启动游戏重写，
//! 上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_aatrox_chain";

/// 本包：被锁住的人身上的标记，名字后面带 `:<圈心x>:<圈心y>:<剑魔>:<到点tick>`。
pub const ON: &str = "league_aatrox_chain_on";
/// 锁住多久：1.5 秒（同主包 w_hold、League）。
pub const HOLD: usize = 90;
/// 数据层读拉回标记的时刻（打中后第几 tick）：本包在 `HOLD` 拉，标记留 `PULL_T` tick。
pub const READ_AT: usize = HOLD + 2;
/// 圈的半径（League 的圈约 460 / W 射程 825，主包 w_area）：横向。
pub const AREA: f64 = 33_000.0;
/// 圈上下的半径：w_ring 画成扁的（锁链外沿横向 ±30 像素、上下 ±20，桩子在 ±33），TFM2 的地面没有透视压扁
/// （1 像素约 1000），正圆的判定上下比画出来的圈多出十几像素——走出画面上的圈锁链也不断。所以按画面判：
/// 横向 `AREA`、上下 `AREA` × 20/30（v0.2.1）。
pub const AREA_Y: f64 = 22_000.0;
/// 找不到锁链时，圈心比他原地往剑魔那边挪多少（League：「稍微靠近剑魔」）。
pub const CENTER_IN: f64 = 3_000.0;
/// 找锁链的范围：打中的那一 tick，剑魔离被打中的人这么近的投射物就是锁链。
pub const FIND_CHAIN: f64 = 20_000.0;
/// 剑魔身上的标记（数据层读）：锁住（播圈）、第一下打中英雄（吸血等）、小兵（再打一下）、拉回（第二下）、
/// 拉回的是英雄（吸血等）。
pub const TETHER: &str = "league_aatrox_w_tether";
pub const CHAMP: &str = "league_aatrox_w_champ";
pub const MINION: &str = "league_aatrox_w_minion";
pub const PULL: &str = "league_aatrox_w_pull";
pub const PULL_C: &str = "league_aatrox_w_pull_c";
/// 标记留多久：打中时的标记数据层同一 tick 和下一 tick 读，拉回的在 `READ_AT` 读。
pub const HIT_T: usize = 3;
/// `w_tether` 留得久一点：数据播圈时把它删掉（RemoveCasterBuff），`watch` 在第 `SEEN_AT` tick 看它还在不在，
/// 写进日志——游戏里「W 看不出」（2026-10-04）时分清是数据没读到本包的标记，还是画面没显示（v0.2.2）。
pub const TETHER_T: usize = 6;
pub const SEEN_AT: usize = 4;
/// 数据没播圈时（`w_tether` 到第 `SEEN_AT` tick 还在），本包自己在圈心播圈，并在被锁的人身上挂这个记号，拉回时
/// 本包再播收紧和缠身（v0.2.3：用户「W 甩出去的锁链看不到 脚下也看不到」，数据读不读得到本包的标记还没证实）。
pub const NATIVE_VIEWS: &str = "league_aatrox_chain_nv";
pub const PULL_T: usize = 6;
/// 拉回的速度（每 tick），到圈心这么近就算到了。
pub const PULL_SPEED: f64 = 2_500.0;
pub const ARRIVE: f64 = 1_500.0;
/// 拉回中：标记前缀；推完后多等几 tick 才算超时；补推一次至少要近这么多，不然算撞墙。
pub const DRAG: &str = "league_aatrox_chain_drag";
pub const DRAG_SLACK: usize = 6;
pub const DRAG_GAIN: f64 = 500.0;
/// 锁链一节一节地飞：每几 tick 一节，每 tick 飞多远；两头往下挪多少（贴地，和圈一样在脚下）。
pub const LINK_EVERY: usize = 4;
pub const LINK_SPEED: u64 = 2_500;
pub const LINK_DROP: f64 = 9_000.0;

/// 主包剑魔的名字（投射物、特效、音效都以它开头）。
fn aatrox(x: &str) -> String {
    format!("league_aatrox_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AATROX_CHAIN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aatrox_chain.log");
        }
    }
    PathBuf::from("league_aatrox_chain.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} {}", m(o.match_id), m(o.set_index), sim.tick(), who(sim, id))
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("#{id} {name}")
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 小工具 =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 在圈外：圈心 `c`，横向半径 `AREA`、上下 `AREA_Y` 的椭圆（和画出来的圈一样）。
pub fn outside(p: (f64, f64), c: (f64, f64)) -> bool {
    ((p.0 - c.0) / AREA).powi(2) + ((p.1 - c.1) / AREA_Y).powi(2) > 1.0
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn pos_of(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| fpos(e.pos()))
}

fn pos_input(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn input_pos(input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect()
    })
}

/// 剑魔身上的短标记（同名的先去掉，免得叠两份）。
fn flag(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn has_cc(sim: &StableSim<'_>, id: usize, kind: CcKindV1) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| c.kind == kind.code())))
}

fn queue(sim: &mut StableSim<'_>, step: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

// ===================== 规则 =====================

/// 找不到锁链时的圈心：他脚下往剑魔那边挪 `CENTER_IN`（剑魔比这还近就只挪一半的距离）。
pub fn center_of(target: (f64, f64), aatrox: Option<(f64, f64)>) -> (f64, f64) {
    let Some(a) = aatrox else { return target };
    let d = dist(target, a);
    if d < 1.0 {
        return target;
    }
    let k = CENTER_IN.min(d / 2.0) / d;
    (target.0 + (a.0 - target.0) * k, target.1 + (a.1 - target.1) * k)
}

/// 锁链停下的地方：剑魔的投射物里离被打中的人最近的那个（`FIND_CHAIN` 以内）。
pub fn impact_point(target: (f64, f64), projectiles: &[(f64, f64)]) -> Option<(f64, f64)> {
    projectiles
        .iter()
        .map(|p| (dist(*p, target), *p))
        .filter(|(d, _)| *d <= FIND_CHAIN)
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, p)| p)
}

/// 标记：`league_aatrox_chain_on:<圈心x>:<圈心y>:<剑魔>:<到点tick>`。
pub fn on_name(center: (f64, f64), aatrox_id: usize, snap: usize) -> String {
    format!("{ON}:{}:{}:{aatrox_id}:{snap}", center.0.round().max(0.0) as u64, center.1.round().max(0.0) as u64)
}

/// 从标记读回 (圈心, 剑魔, 到点tick)。
pub fn parse_on(name: &str) -> Option<((f64, f64), usize, usize)> {
    let mut it = name.strip_prefix(ON)?.strip_prefix(':')?.split(':');
    let x: u64 = it.next()?.parse().ok()?;
    let y: u64 = it.next()?.parse().ok()?;
    let a: usize = it.next()?.parse().ok()?;
    let snap: usize = it.next()?.parse().ok()?;
    it.next().is_none().then_some(((x as f64, y as f64), a, snap))
}

/// 被锁链打中的是什么。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Champion,
    /// 野怪（中立；TFM2 的 rhino / mushroom / stump / bee / serpen / epic_monster 都是单只的大怪）。
    Monster,
    Minion,
    /// 塔、召唤物：不拴。
    Other,
}

pub fn kind_of(champion: bool, minion: bool, tower: bool, team: usize, name: &str) -> Kind {
    if champion {
        Kind::Champion
    } else if tower {
        Kind::Other
    } else if name.contains("monster") || team > 1 {
        Kind::Monster
    } else if minion {
        Kind::Minion
    } else {
        Kind::Other
    }
}

// ===================== 打中 =====================

/// 锁链打中的单位：数据层给的目标；给的是位置时，找那附近刚被 W 减速的敌人。
fn hit_unit(sim: &StableSim<'_>, me: usize, input: &InputTargetV1) -> Option<usize> {
    if input.kind == InputTargetKindV1::Target.code() {
        return Some(input.target_id);
    }
    let at = input_pos(input).or_else(|| pos_of(sim, me))?;
    let team = sim.get_entity(me)?.team();
    let slowed = aatrox("w_slowed");
    let mut best: Option<(f64, usize)> = None;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || e.is_tower() {
            continue;
        }
        let d = dist(at, fpos(e.pos()));
        if d <= 15_000.0 && best.is_none_or(|b| d < b.0) && names(sim, e.id()).contains(&slowed) {
            best = Some((d, e.id()));
        }
    }
    best.map(|b| b.1)
}

fn chain(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(t) = hit_unit(sim, me, &input) else {
        wlog(format!("{} chain hit: no unit (input kind {})", head(sim, me), input.kind));
        return;
    };
    let Some(e) = sim.get_entity(t) else { return };
    let living = e.is_alive();
    let name = e.name().unwrap_or_default();
    match kind_of(e.is_champion(), e.is_minion(), e.is_tower(), e.team(), &name) {
        Kind::Minion => flag(sim, me, MINION, HIT_T),
        Kind::Champion => {
            // 主包把第一下的吸血等挂在「锁链旁边的英雄」上（小兵挡住时也会算到后面的英雄），本包按真正打中的人来
            flag(sim, me, CHAMP, HIT_T);
            if living {
                tether(sim, me, t, Kind::Champion);
            }
        }
        Kind::Monster if living => tether(sim, me, t, Kind::Monster),
        Kind::Monster => {}
        Kind::Other => wlog(format!("{} chain hit {}: not tethered", head(sim, me), who(sim, t))),
    }
}

/// 锁住：圈心是锁链停下的地方，标记、第一节锁链、剑魔身上的 `w_tether`（数据播圈），开始每 tick 看着他。
fn tether(sim: &mut StableSim<'_>, me: usize, t: usize, kind: Kind) {
    if names(sim, t).iter().filter_map(|n| parse_on(n)).any(|(_, a, _)| a == me) {
        return;
    }
    let Some(here) = pos_of(sim, t) else { return };
    let from = pos_of(sim, me);
    let mine: Vec<(f64, f64)> = (0..sim.projectile_count())
        .filter_map(|i| sim.projectile_at(i))
        .filter(|p| p.caster_id == me)
        .map(|p| (p.x as f64, p.y as f64))
        .collect();
    let found = impact_point(here, &mine);
    let c = found.unwrap_or_else(|| center_of(here, from));
    let snap = sim.tick() + HOLD;
    sim.add_buff(t, &BuffV1::timed(&on_name(c, me, snap), HOLD + 5));
    flag(sim, me, TETHER, TETHER_T);
    let linked = link(sim, me, here, c);
    queue(sim, "watch", t, pos_input(c), 1);
    wlog(format!(
        "{} TETHER {kind:?} {} at {} ring {} ({}; Aatrox {}){}",
        head(sim, me),
        who(sim, t),
        pt(here),
        pt(c),
        if found.is_some() { "the chain's stop" } else { "no chain found: 3000 toward Aatrox" },
        from.map_or("-".to_string(), pt),
        if linked { "" } else { " - spawn_projectile(w_link) refused" }
    ));
}

/// 一节锁链：从他脚下飞向圈心，贴着地面（两头往下挪 `LINK_DROP`）；看不见的碰撞，什么都不打。
fn link(sim: &mut StableSim<'_>, me: usize, from: (f64, f64), c: (f64, f64)) -> bool {
    if dist(from, c) < 2_000.0 {
        return true;
    }
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: from.0.round().max(0.0) as u64,
        y: (from.1 + LINK_DROP).round().max(0.0) as u64,
        radius: 1_000,
        speed: LINK_SPEED,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: c.0.round().max(0.0) as u64,
        target_y: (c.1 + LINK_DROP).round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(&aatrox("w_link"), &format!("{ID}:noop"), &spec)
}

// ===================== 拴着 =====================

/// 每 tick（`me` = 被锁住的人，输入 = 圈心）：走出圈就断；到点还在圈里就拉回。
fn watch(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(at) = input_pos(&input) else { return };
    let mark = names(sim, me).into_iter().find_map(|n| {
        let (c, a, snap) = parse_on(&n)?;
        (dist(c, at) < 2.0).then_some((n, c, a, snap))
    });
    let Some((name, c, a, snap)) = mark else { return };
    let tick = sim.tick();
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() {
        sim.entity_remove_buff(me, &name);
        wlog(format!("{} died while chained", head(sim, me)));
        return;
    }
    let here = fpos(e.pos());
    let d = dist(here, c);
    if HOLD.saturating_sub(snap.saturating_sub(tick)) == SEEN_AT {
        let left = names(sim, a).iter().any(|n| n == TETHER);
        let mut took = true;
        if left {
            sim.entity_remove_buff(a, TETHER);
            took = sim.play_view_effect(&aatrox("w_ring"), a, &pos_input(c), 0, 0, 0);
            sim.play_sfx(&aatrox("w_ring"), a, &pos_input(c));
            sim.add_buff(me, &BuffV1::timed(NATIVE_VIEWS, HOLD + 5));
        }
        wlog(format!("{} RING {}: the data {} the w_tether flag", head(sim, me),
                     if left { if took { "NOT PLAYED by the data, played here" } else { "NOT PLAYED by the data, refused here" } }
                     else { "played by the data" },
                     if left { "did not read" } else { "read and removed" }));
    }
    if outside(here, c) {
        sim.entity_remove_buff(me, &name);
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&aatrox("w_hit"), a, &on_me, 0, 0, 0);
        sim.play_sfx(&aatrox("w_hit"), a, &on_me);
        wlog(format!("{} BREAK: {d:.0} from the ring's centre ({:+.0}, {:+.0}), {} ticks before the pull", head(sim, me),
                     here.0 - c.0, here.1 - c.1, snap.saturating_sub(tick)));
        return;
    }
    if tick >= snap {
        sim.entity_remove_buff(me, &name);
        pull(sim, me, c, a, d);
        return;
    }
    let age = HOLD.saturating_sub(snap - tick);
    if age % LINK_EVERY == 0 {
        link(sim, a, here, c);
    }
    queue(sim, "watch", me, input, 1);
}

/// 到点还在圈里：剑魔身上挂 `w_pull`（英雄再挂 `w_pull_c`），数据在 `READ_AT` 打第二下、播收紧和缠身；
/// 他被拉回圈心。
fn pull(sim: &mut StableSim<'_>, me: usize, c: (f64, f64), a: usize, d: f64) {
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_targetable() {
        wlog(format!("{} PULL skipped: untargetable at the pull", head(sim, me)));
        return;
    }
    let champion = e.is_champion();
    let marked = alive(sim, a);
    if names(sim, me).iter().any(|n| n == NATIVE_VIEWS) {
        // the data missed the ring: the snap and the wrap played here too
        sim.entity_remove_buff(me, NATIVE_VIEWS);
        sim.play_view_effect(&aatrox("w_snap"), a, &pos_input(c), 0, 0, 0);
        sim.play_view_effect(&aatrox("w_yank"), a, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx(&aatrox("w_yank"), a, &InputTargetV1::target(me));
    }
    if marked {
        flag(sim, a, PULL, PULL_T);
        if champion {
            flag(sim, a, PULL_C, PULL_T);
        }
    }
    let mut ticks = 0;
    if d > ARRIVE {
        if let Some(here) = pos_of(sim, me) {
            ticks = push(sim, me, here, c, d);
        }
    }
    wlog(format!(
        "{} PULL: {d:.0} from the centre, pulled in {ticks} ticks; {}",
        head(sim, me),
        if marked { "the second hit flagged on Aatrox" } else { "Aatrox is dead: no second hit" }
    ));
}

/// 强制位移到 `to`，正好走到（速度取整到每 tick 一样长）；返回 tick 数。
fn force_move(sim: &mut StableSim<'_>, id: usize, from: (f64, f64), to: (f64, f64), speed: f64) -> usize {
    let d = dist(from, to);
    if d < 1.0 {
        return 0;
    }
    let ticks = (d / speed).ceil().max(1.0);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(id, &cc);
    ticks as usize
}

/// 拉回中的标记：`league_aatrox_chain_drag:<上次推的时候离圈心多远>`。
pub fn drag_name(d: f64) -> String {
    format!("{DRAG}:{}", d.round().max(0.0) as u64)
}

pub fn parse_drag(name: &str) -> Option<f64> {
    name.strip_prefix(DRAG)?.strip_prefix(':')?.parse::<u64>().ok().map(|d| d as f64)
}

/// 开始推（拉回、补推）：强制位移 + 标记，推完下一 tick 看一眼。
fn push(sim: &mut StableSim<'_>, me: usize, here: (f64, f64), c: (f64, f64), d: f64) -> usize {
    let ticks = force_move(sim, me, here, c, PULL_SPEED);
    sim.add_buff(me, &BuffV1::timed(&drag_name(d), ticks + DRAG_SLACK));
    queue(sim, "drag", me, pos_input(c), ticks + 1);
    ticks
}

/// 推完了：到了就结束；还差得远（韧性把强制位移截短了）就再推剩下的路；比上次没近多少（撞墙了）就算了。
fn drag(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let (Some(c), Some(here)) = (input_pos(&input), pos_of(sim, me)) else { return };
    let Some((name, last)) = names(sim, me).into_iter().find_map(|n| parse_drag(&n).map(|l| (n, l))) else { return };
    let d = dist(here, c);
    if !alive(sim, me) || d <= ARRIVE {
        sim.entity_remove_buff(me, &name);
        return;
    }
    if has_cc(sim, me, CcKindV1::ForceMove) {
        queue(sim, "drag", me, input, 1);
        return;
    }
    sim.entity_remove_buff(me, &name);
    if d > last - DRAG_GAIN {
        wlog(format!("{} DRAG stuck {d:.0} short of the centre (was {last:.0}): a wall or cc-immune", head(sim, me)));
        return;
    }
    let ticks = push(sim, me, here, c, d);
    wlog(format!("{} DRAG: stopped {d:.0} short of the centre, pushed again for {ticks} ticks", head(sim, me)));
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Chain,
    Watch,
    Drag,
    Noop,
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Chain => chain(sim, caster, input),
            Step::Watch => watch(sim, caster, input),
            Step::Drag => drag(sim, caster, input),
            Step::Noop => {}
        }
    }
}

/// 本包的原生效果：`league_aatrox_chain:<名字>`。数据层只调 `chain`。
pub const STAGES: [&str; 4] = ["chain", "watch", "drag", "noop"];

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (League's Infernal Chains; pictures and hits in data) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.add_native_effect(format!("{ID}:chain"), Stage(Step::Chain));
    module.add_native_effect(format!("{ID}:watch"), Stage(Step::Watch));
    module.add_native_effect(format!("{ID}:drag"), Stage(Step::Drag));
    module.add_native_effect(format!("{ID}:noop"), Stage(Step::Noop));
    host.log(LogLevel::Info, "league_aatrox_chain v0.2 loaded (Aatrox's W tethers the unit it hits, breaks outside the ring, pulls back at 1.5 s).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_mark_carries_centre_aatrox_and_the_pull_tick() {
        let name = on_name((412_345.4, 98_765.6), 41, 123_456);
        assert_eq!(name, "league_aatrox_chain_on:412345:98766:41:123456");
        assert_eq!(parse_on(&name), Some(((412_345.0, 98_766.0), 41, 123_456)));
        assert_eq!(parse_on(ON), None);
        assert_eq!(parse_on("league_aatrox_chain_on:1:2:3"), None);
        assert_eq!(parse_on("league_aatrox_chain_on:1:2:3:4:5"), None);
        assert_eq!(parse_on("league_aatrox_w_slowed"), None);
        // 名字放得下（buff 名最多 64 字节）：地图约 960000，实体 id、tick 都远小于 u32::MAX
        assert!(on_name((9_999_999.0, 9_999_999.0), u32::MAX as usize, u32::MAX as usize).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_drag_mark_keeps_the_last_distance() {
        assert_eq!(drag_name(27_000.4), "league_aatrox_chain_drag:27000");
        assert_eq!(parse_drag("league_aatrox_chain_drag:27000"), Some(27_000.0));
        assert_eq!(parse_drag(DRAG), None);
        assert_eq!(parse_drag("league_aatrox_chain_on:1:2:3:4"), None);
    }

    #[test]
    fn the_ring_sits_where_the_chain_stopped() {
        // 剑魔的投射物里离他最近的（20000 以内）是锁链
        let target = (100_000.0, 50_000.0);
        assert_eq!(impact_point(target, &[(90_000.0, 47_000.0), (60_000.0, 50_000.0)]), Some((90_000.0, 47_000.0)));
        assert_eq!(impact_point(target, &[(60_000.0, 50_000.0)]), None);
        assert_eq!(impact_point(target, &[]), None);
        // 找不到：往剑魔那边挪 3000（剑魔贴着他就挪一半）
        assert_eq!(center_of((100_000.0, 0.0), Some((50_000.0, 0.0))), (97_000.0, 0.0));
        assert_eq!(center_of((10_000.0, 0.0), Some((6_000.0, 0.0))), (8_000.0, 0.0));
        assert_eq!(center_of((10_000.0, 5.0), None), (10_000.0, 5.0));
    }

    #[test]
    fn what_gets_tethered() {
        assert_eq!(kind_of(true, false, false, 1, "league_garen"), Kind::Champion);
        assert_eq!(kind_of(false, true, false, 1, "melee_minion"), Kind::Minion);
        assert_eq!(kind_of(false, false, false, 2, "rhino_monster"), Kind::Monster);
        // 野怪就算宿主把它当小兵、或队伍码不是中立：按名字也算野怪
        assert_eq!(kind_of(false, true, false, 2, "serpen_monster"), Kind::Monster);
        assert_eq!(kind_of(false, false, false, 0, "epic_monster"), Kind::Monster);
        assert_eq!(kind_of(false, false, true, 1, "tower"), Kind::Other);
        // 召唤物（安妮的熊之类）不拴
        assert_eq!(kind_of(false, false, false, 1, "league_annie_tibbers"), Kind::Other);
        // 数据层读拉回标记时，标记还在
        assert!(READ_AT > HOLD && READ_AT < HOLD + PULL_T);
    }
}
