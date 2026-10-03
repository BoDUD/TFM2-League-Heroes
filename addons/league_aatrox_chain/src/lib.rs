//! 剑魔 W 锁链附加包：W「恶火束链」照 League 原版。
//!
//! 主包的 W（数据）：锁链停在第一个敌人身上（伤害 + 减速 1.5 秒）；打中英雄时在落点放圈，1.5 秒后那个英雄
//! 再受一次伤害、被拉向剑魔。League 的两条数据写不出来：走出圈锁链就断、拉回的是圈的中心。
//! `mod.override_info` 把主包的剑魔换成 `override/` 里的副本：锁链打中的那一下调本包的 `chain`，主包的
//! 第二下（英雄身上的 `Delayed`）和落点的圈去掉，其余不动。
//!
//! - `chain`（锁链打中谁就对谁调，League：只有这一个人）：
//!   - 英雄或野怪（League：英雄和大型野怪；TFM2 的野怪都是单只的大怪）：圈放在他脚下往剑魔那边挪
//!     `CENTER_IN` 的地方（League：拉回的位置比原地稍微靠近剑魔），半径 `AREA`（League 的圈约 460、W 射程 825，
//!     本包 W 射程 60000），他身上挂 `league_aatrox_chain_on:<圈心x>:<圈心y>:<剑魔>:<到点tick>`，
//!     然后每 tick 看着他（`watch`，以他为施法者排队，剑魔死了也照样跑）。
//!   - 小兵：再受一次同样的伤害（League：对小兵双倍）。
//! - `watch`：离圈心超过 `AREA`（走出去、闪现、冲刺都算）→ 锁链断，什么都不发生；到 `HOLD` tick（1.5 秒）
//!   还在圈里 → 再受一次伤害（按剑魔当下的攻击力算），拉回圈心（引擎的强制位移 ForceMove，撞墙会停）；
//!   英雄的话照主包的规矩：剑魔吸血（E 被动，大灭期间更多）、记一次被动冷却缩减、大灭期间记击杀
//!   （第一下打中英雄时也一样，按锁链真正打中的人算）。
//!   拴着的时候每 `LINK_EVERY` tick 从他脚下往圈心飞一节锁链（`league_aatrox_w_link`），
//!   圈每 `RING_BEAT` tick 补播一次，锁链断了就不再补。
//! - `drag`：拉回被韧性截短了就再推剩下的路，直到到圈心；比上次没近多少（撞墙）就停。
//! - `kill`：大灭期间第二下之后一 tick 看他死了没（引擎的死亡可能在这一 tick 末才算）。
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
/// 圈的半径（League 的圈约 460 / W 射程 825，主包 w_area）。
pub const AREA: f64 = 33_000.0;
/// 圈心比他原地往剑魔那边挪多少（League：「稍微靠近剑魔」）。
pub const CENTER_IN: f64 = 3_000.0;
/// 伤害（同主包 w_dmg / w_ratio）：40 + 40% 攻击力，第二下一样，对小兵再来一次。
pub const W_DMG: usize = 40;
pub const W_RATIO: usize = 40;
/// W 打中英雄时剑魔回的血（主包 E 被动的 amp：40 + 40% 的 18%，大灭期间 ×1.5，取整同主包）：数额 + 攻击力%。
pub const E_HEAL_AMOUNT: usize = 7;
pub const E_HEAL_RATIO: usize = 7;
pub const E_HEAL_R_AMOUNT: usize = 10;
pub const E_HEAL_R_RATIO: usize = 10;
/// 被动冷却缩减的欠条（主包 pc1..pc3，pc_hold）。
pub const PC_HOLD: usize = 900;
/// 大灭的击杀标记（主包 k_b 的时长）。
pub const K_HOLD: usize = 6;
/// 拉回的速度（每 tick），到圈心这么近就算到了。
pub const PULL_SPEED: f64 = 2_500.0;
pub const ARRIVE: f64 = 1_500.0;
/// 拉回中：标记前缀；推完后多等几 tick 才算超时；补推一次至少要近这么多，不然算撞墙。
pub const DRAG: &str = "league_aatrox_chain_drag";
pub const DRAG_SLACK: usize = 6;
pub const DRAG_GAIN: f64 = 500.0;
/// 锁链一节一节地飞：每几 tick 一节，每 tick 飞多远。
pub const LINK_EVERY: usize = 4;
pub const LINK_SPEED: u64 = 2_500;
/// 圈的画面：`w_ring_in`（出现 + 一圈）多长，之后每 `RING_BEAT` tick 补播一次 `w_ring_beat`
/// （同 tools/art/import_aatrox.py 里两段动画的长度）。
pub const RING_IN: usize = 24;
pub const RING_BEAT: usize = 16;

/// 主包剑魔的名字（buff、特效、音效都以它开头）。
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

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    names(sim, id).iter().any(|n| n == name)
}

fn refresh(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
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

/// 圈心：他脚下往剑魔那边挪 `CENTER_IN`（剑魔比这还近就只挪一半的距离）；不知道剑魔在哪就在他脚下。
pub fn center_of(target: (f64, f64), aatrox: Option<(f64, f64)>) -> (f64, f64) {
    let Some(a) = aatrox else { return target };
    let d = dist(target, a);
    if d < 1.0 {
        return target;
    }
    let k = CENTER_IN.min(d / 2.0) / d;
    (target.0 + (a.0 - target.0) * k, target.1 + (a.1 - target.1) * k)
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

/// 一下 W 的伤害（第一下、第二下、对小兵补的那下都一样）：`W_DMG` + `W_RATIO`% 攻击力。
pub fn w_damage(attack: usize) -> usize {
    W_DMG + attack * W_RATIO / 100
}

/// W 打中英雄时剑魔回的血（攻击力 `attack`，`ult` = 大灭期间）。
pub fn e_heal(attack: usize, ult: bool) -> usize {
    let (amount, ratio) = if ult { (E_HEAL_R_AMOUNT, E_HEAL_R_RATIO) } else { (E_HEAL_AMOUNT, E_HEAL_RATIO) };
    amount + attack * ratio / 100
}

/// 被锁链打中的是什么。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Champion,
    /// 野怪（中立；TFM2 的 rhino / mushroom / stump / bee / serpen_monster 都是单只的大怪）。
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

/// 拴着的第 `age` tick（锁链打中那一 tick 是 0）要不要补播圈：出现那段放完后每 `RING_BEAT` tick 一次，
/// 播到超过到点半段以上的那次不播（到点时播收紧的画面）。
pub fn ring_beat_due(age: usize) -> bool {
    age >= RING_IN && (age - RING_IN) % RING_BEAT == 0 && age + RING_BEAT <= HOLD + RING_BEAT / 2
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
        Kind::Minion if living => {
            let dmg = w_damage(sim.get_entity(me).map_or(0, |a| a.stat().attack));
            sim.deal_damage(me, t, dmg, 0, AttackTypeV1::Skill);
        }
        Kind::Champion => {
            // 主包把这段挂在「锁链旁边的英雄」上（小兵挡住时也会算到后面的英雄），本包按真正打中的人来
            let extra = on_champion(sim, me, t);
            if living {
                tether(sim, me, t, Kind::Champion);
            } else {
                wlog(format!("{} chain hit killed {}{extra}", head(sim, me), who(sim, t)));
            }
        }
        Kind::Monster if living => tether(sim, me, t, Kind::Monster),
        Kind::Other => wlog(format!("{} chain hit {}: not tethered", head(sim, me), who(sim, t))),
        _ => {}
    }
}

/// 锁住：圈、标记、第一节锁链，开始每 tick 看着他。
fn tether(sim: &mut StableSim<'_>, me: usize, t: usize, kind: Kind) {
    if names(sim, t).iter().filter_map(|n| parse_on(n)).any(|(_, a, _)| a == me) {
        return;
    }
    let Some(here) = pos_of(sim, t) else { return };
    let from = pos_of(sim, me);
    let c = center_of(here, from);
    let snap = sim.tick() + HOLD;
    sim.add_buff(t, &BuffV1::timed(&on_name(c, me, snap), HOLD + 5));
    let at_c = pos_input(c);
    sim.play_view_effect(&aatrox("w_ring_in"), me, &at_c, 0, 0, 0);
    sim.play_sfx(&aatrox("w_ring"), me, &at_c);
    let linked = link(sim, me, here, c);
    queue(sim, "watch", t, at_c, 1);
    wlog(format!(
        "{} TETHER {kind:?} {} at {} ring {} (Aatrox {}){}",
        head(sim, me),
        who(sim, t),
        pt(here),
        pt(c),
        from.map_or("-".to_string(), pt),
        if linked { "" } else { " - spawn_projectile(w_link) refused" }
    ));
}

/// 一节锁链：从他脚下飞向圈心（看不见的碰撞，什么都不打）。
fn link(sim: &mut StableSim<'_>, me: usize, from: (f64, f64), c: (f64, f64)) -> bool {
    if dist(from, c) < 2_000.0 {
        return true;
    }
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: from.0.round().max(0.0) as u64,
        y: from.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: LINK_SPEED,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: c.0.round().max(0.0) as u64,
        target_y: c.1.round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(&aatrox("w_link"), &format!("{ID}:noop"), &spec)
}

// ===================== 拴着 =====================

/// 每 tick（`me` = 被锁住的人，输入 = 圈心）：走出圈就断；到点还在圈里就拉回、再打一下。
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
    if d > AREA {
        sim.entity_remove_buff(me, &name);
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&aatrox("w_hit"), a, &on_me, 0, 0, 0);
        sim.play_sfx(&aatrox("w_hit"), a, &on_me);
        wlog(format!("{} BREAK: {d:.0} from the ring's centre, {} ticks before the pull", head(sim, me), snap.saturating_sub(tick)));
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
    if ring_beat_due(age) {
        sim.play_view_effect(&aatrox("w_ring_beat"), a, &input, 0, 0, 0);
    }
    queue(sim, "watch", me, input, 1);
}

/// 到点还在圈里：收紧的画面，再受一次伤害，拉回圈心；英雄的话照主包第二下的规矩记吸血、被动、击杀。
fn pull(sim: &mut StableSim<'_>, me: usize, c: (f64, f64), a: usize, d: f64) {
    let at_c = pos_input(c);
    let on_me = InputTargetV1::target(me);
    sim.play_view_effect(&aatrox("w_snap"), a, &at_c, 0, 0, 0);
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_targetable() {
        wlog(format!("{} PULL skipped: untargetable at the pull", head(sim, me)));
        return;
    }
    let champion = e.is_champion();
    let before = e.hp().0;
    let dmg = w_damage(sim.get_entity(a).map_or(0, |x| x.stat().attack));
    sim.deal_damage(a, me, dmg, 0, AttackTypeV1::Skill);
    sim.play_view_effect(&aatrox("w_yank"), a, &on_me, 0, 0, 0);
    sim.play_sfx(&aatrox("w_yank"), a, &on_me);
    let (after, max) = sim.get_entity(me).map_or((0, 0), |x| x.hp());
    let mut extra = String::new();
    if champion {
        extra = on_champion(sim, a, me);
    }
    let mut ticks = 0;
    if alive(sim, me) && d > ARRIVE {
        if let Some(here) = pos_of(sim, me) {
            ticks = push(sim, me, here, c, d);
        }
    }
    wlog(format!(
        "{} PULL: {d:.0} from the centre, pulled in {ticks} ticks, hit {dmg} ({before} -> {after}/{max}){extra}",
        head(sim, me)
    ));
}

/// W 打中英雄（第一下、第二下各一次，同主包 on_champ）：剑魔吸血、欠被动一次冷却缩减（pc1 → pc2 → pc3，
/// 他下次普攻时扣）、大灭期间记击杀。
fn on_champion(sim: &mut StableSim<'_>, a: usize, t: usize) -> String {
    let ult = has_buff(sim, a, &aatrox("r"));
    let mut out = String::new();
    if alive(sim, a) {
        let heal = e_heal(sim.get_entity(a).map_or(0, |x| x.stat().attack), ult);
        sim.heal(a, a, heal);
        out += &format!(", Aatrox heals {heal}");
    }
    let held = names(sim, a);
    let pc = if held.contains(&aatrox("pc2")) {
        "pc3"
    } else if held.contains(&aatrox("pc1")) {
        "pc2"
    } else {
        "pc1"
    };
    refresh(sim, a, &aatrox(pc), PC_HOLD);
    out += &format!(", passive cut {pc}");
    if ult {
        if alive(sim, t) && sim.get_entity(t).is_some_and(|e| e.hp().0 > 0) {
            queue(sim, "kill", a, InputTargetV1::target(t), 1);
        } else {
            mark_kill(sim, a);
            out += ", KILL in World Ender";
        }
    }
    out
}

/// 主包大灭的击杀检查：k_b 在、k_a 不在 = 他打的英雄死了，大灭刷新。
fn mark_kill(sim: &mut StableSim<'_>, a: usize) {
    sim.entity_remove_buff(a, &aatrox("k_a"));
    refresh(sim, a, &aatrox("k_b"), K_HOLD);
}

fn kill(sim: &mut StableSim<'_>, a: usize, input: InputTargetV1) {
    if input.kind != InputTargetKindV1::Target.code() || alive(sim, input.target_id) || !has_buff(sim, a, &aatrox("r")) {
        return;
    }
    mark_kill(sim, a);
    wlog(format!("{} KILL in World Ender: {} died after the pull", head(sim, a), who(sim, input.target_id)));
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
        wlog(format!("{} DRAG stuck {d:.0} short of the centre (was {last:.0}): a wall?", head(sim, me)));
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
    Kill,
    Noop,
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Chain => chain(sim, caster, input),
            Step::Watch => watch(sim, caster, input),
            Step::Drag => drag(sim, caster, input),
            Step::Kill => kill(sim, caster, input),
            Step::Noop => {}
        }
    }
}

/// 本包的原生效果：`league_aatrox_chain:<名字>`。数据层只调 `chain`。
pub const STAGES: [&str; 5] = ["chain", "watch", "drag", "kill", "noop"];

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v0.1 (League's Infernal Chains) loaded: game {}.{}.{} abi {} log={} ===",
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
    module.add_native_effect(format!("{ID}:kill"), Stage(Step::Kill));
    module.add_native_effect(format!("{ID}:noop"), Stage(Step::Noop));
    host.log(LogLevel::Info, "league_aatrox_chain loaded (Aatrox's W tethers the unit it hits, breaks outside the ring, pulls back at 1.5 s).");
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
    fn the_ring_sits_a_little_toward_aatrox() {
        // 剑魔在左边 50000：圈心往左挪 3000
        assert_eq!(center_of((100_000.0, 0.0), Some((50_000.0, 0.0))), (97_000.0, 0.0));
        // 斜着：挪的距离还是 3000
        let c = center_of((0.0, 0.0), Some((30_000.0, 40_000.0)));
        assert!((dist(c, (0.0, 0.0)) - CENTER_IN).abs() < 1e-6 && c.0 > 0.0 && c.1 > 0.0);
        // 剑魔贴着他（4000）：只挪一半；剑魔不在 / 重合：原地
        assert_eq!(center_of((10_000.0, 0.0), Some((6_000.0, 0.0))), (8_000.0, 0.0));
        assert_eq!(center_of((10_000.0, 5.0), None), (10_000.0, 5.0));
        assert_eq!(center_of((10_000.0, 5.0), Some((10_000.0, 5.0))), (10_000.0, 5.0));
    }

    #[test]
    fn damage_heal_and_what_gets_tethered() {
        assert_eq!(w_damage(100), 80);
        assert_eq!(w_damage(0), W_DMG);
        // 7 + 7% 攻击力，大灭期间 10 + 10%（同主包）
        assert_eq!(e_heal(100, false), 14);
        assert_eq!(e_heal(125, true), 22);
        assert_eq!(kind_of(true, false, false, 1, "league_garen"), Kind::Champion);
        assert_eq!(kind_of(false, true, false, 1, "melee_minion"), Kind::Minion);
        assert_eq!(kind_of(false, false, false, 2, "rhino_monster"), Kind::Monster);
        // 野怪就算宿主把它当小兵、或队伍码不是中立：按名字也算野怪
        assert_eq!(kind_of(false, true, false, 2, "serpen_monster"), Kind::Monster);
        assert_eq!(kind_of(false, false, false, 0, "bee_monster"), Kind::Monster);
        assert_eq!(kind_of(false, false, true, 1, "tower"), Kind::Other);
        // 召唤物（安妮的熊之类）不拴
        assert_eq!(kind_of(false, false, false, 1, "league_annie_tibbers"), Kind::Other);
    }

    #[test]
    fn the_ring_is_replayed_until_the_pull() {
        let beats: Vec<usize> = (0..=HOLD).filter(|a| ring_beat_due(*a)).collect();
        assert_eq!(beats, [24, 40, 56, 72]);
        // 最后一次播到 88，到点（90）播收紧的画面
        assert!(beats.last().unwrap() + RING_BEAT <= HOLD);
    }
}
