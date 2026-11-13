//! 推人、拉人的共用规则（2026-11-13，用户：「沙皇的反推 好像推不到人 整体检查一下各个推的逻辑」「接着修」）。
//!
//! - **韧性**：引擎把每种控制的时长按目标的韧性缩短，x (100 - 韧性) / 100，强制位移（击退、拉人、拖人、冲刺都是 ForceMove）
//!   也一样（`.claude/skills/tfm2-hero-mod/references/champion-data.md`，读的 game_core）。强制位移走的是「速度 x tick」，tick
//!   短了路就短：带 30% 韧性的人只被推出七成（4+6 的出装里 66 个英雄有 20%～30% 韧性的装备）。英雄联盟的位移不吃韧性。
//!   - 附加包自己推、拉的：按目标的韧性把时长放长，缩短以后正好走满（[`full_ticks`]；[`force_move_full`]、
//!     [`knockback_full`]、[`grab_full`]、[`pull_full`]），目标身上挂 [`FULL`]，说明这一下已经放长过。
//!   - 别的（数据里的击退、引擎的击退和拉、英雄自己的冲刺）：合集的比赛钩子每 tick 调 [`keep_tick`]：英雄身上出现一个没挂
//!     [`FULL`] 的强制位移、他又有韧性，就按看到的剩余时长算出被截掉的那一截，记在他身上（[`Keep`] 的 buff 名字）；
//!     这一下走完（到点了，不是被控制打断的）就按原方向、原速度把那一截补上（放长过，挂 [`FULL`]）。日志
//!     `league_push.log`（每次启动重写，上一次的留在 .prev.log）：每补一次一行 `KEEP`。
//! - **击飞打断位移**（同一份笔记）：给正在位移的单位上击飞，位移就停了——要一起上，先击飞再推。
//! - **被按住的不挪**：眩晕、定身、击飞、嘲讽、恐惧、魅惑（[`HELD`]，李青 W 的 `HELD`）时宿主停下他的强制位移；被按住打断的
//!   一下不补。
//!
//! 推人的附加包靠「到点就算到了」的（撞墙晕）先看他是不是真的到了（[`moving`] / 各包自己的落点）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::Mutex;

use mod_api_stable::*;

/// 按住一个单位、宿主停下他的强制位移的控制。
pub const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

/// 这一下强制位移已经按韧性放长过（附加包推的、[`keep_tick`] 补的）：[`keep_tick`] 不再管它。
pub const FULL: &str = "push_full";
/// [`Keep`] 的 buff 名字的开头。
pub const KEEP: &str = "push_keep:";
/// [`keep_tick`] 只管这么长以内的强制位移（10 秒）：更长的（0 = 拽到为止之类）不是韧性截短的那种。
pub const MAX_TRACK: usize = 600;

/// 他身上所有效果的韧性加起来（4+6 的装备、符文、技能的 buff）。
pub fn toughness(u: &StableEntity<'_, '_>) -> usize {
    (0..u.buff_count()).filter_map(|i| u.buff_at(i)).map(|b| b.toughness).sum()
}

/// `id` 的韧性（找不到他就是 0）。
pub fn toughness_of(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |u| toughness(&u))
}

/// 要一个控制在目标身上留满 `ticks`，按他的韧性 `toughness` 放长到的时长：引擎乘 (100 - 韧性) / 100，放长到
/// ceil(ticks x 100 / (100 - 韧性))，缩短以后不少于 `ticks`。韧性到 100 的什么控制都留不住：None。
pub fn full_ticks(ticks: usize, toughness: usize) -> Option<usize> {
    let keep = 100usize.saturating_sub(toughness);
    (keep > 0).then(|| (ticks * 100).div_ceil(keep))
}

/// 引擎缩短以后剩 `seen` tick 的一个控制，原来大约多长：ceil(seen x 100 / (100 - 韧性))（韧性到 100 的：`seen`）。
pub fn uncut_ticks(seen: usize, toughness: usize) -> usize {
    let keep = 100usize.saturating_sub(toughness);
    if keep == 0 { seen } else { (seen * 100).div_ceil(keep) }
}

fn mark(sim: &mut StableSim<'_>, id: usize, ticks: usize) {
    sim.entity_remove_buff(id, FULL);
    sim.add_buff(id, &BuffV1::timed(FULL, ticks + 2));
}

/// 强制位移 `cc`（ForceMove：`dx`/`dy` 定方向，速度 x tick 是路），按 `id` 的韧性放长时长；韧性到 100 的不推，返回 false。
pub fn force_move_full(sim: &mut StableSim<'_>, id: usize, mut cc: CcV1) -> bool {
    let Some(ticks) = full_ticks(cc.tick as usize, toughness_of(sim, id)) else { return false };
    cc.tick = ticks as u64;
    sim.apply_cc(id, &cc);
    mark(sim, id, ticks);
    true
}

/// 引擎的击退（从 `caster` 往外推 `speed` x `ticks`），按 `target` 的韧性放长。
pub fn knockback_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let Some(t) = full_ticks(ticks, toughness_of(sim, target)) else { return false };
    let ok = sim.entity_knockback(caster, target, speed, t);
    mark(sim, target, t);
    ok
}

/// 引擎的抓（往 `caster` 拽，`ticks` 是 0 就一直拽到），按 `target` 的韧性放长；拽到为止的不用放长。
pub fn grab_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let t = if ticks == 0 { Some(0) } else { full_ticks(ticks, toughness_of(sim, target)) };
    let Some(t) = t else { return false };
    let ok = sim.entity_grab(caster, target, speed, t);
    mark(sim, target, if t == 0 { MAX_TRACK } else { t });
    ok
}

/// 引擎的拉（往 `caster` 拉 `speed` x `ticks`），按 `target` 的韧性放长。
pub fn pull_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let Some(t) = full_ticks(ticks, toughness_of(sim, target)) else { return false };
    let ok = sim.entity_pull(caster, target, speed, t);
    mark(sim, target, t);
    ok
}

fn has_kind(u: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> bool {
    (0..u.cc_count()).any(|i| u.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

/// 被按住（[`HELD`]）。
pub fn held(u: &StableEntity<'_, '_>) -> bool {
    has_kind(u, &HELD)
}

/// 还在强制位移。
pub fn moving(u: &StableEntity<'_, '_>) -> bool {
    has_kind(u, &[CcKindV1::ForceMove])
}

/// `id` 还在强制位移（找不到他就不是）。
pub fn moving_id(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|u| moving(&u))
}

/// `id` 被按住（找不到他就不是）。
pub fn held_id(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|u| held(&u))
}

/// 一个被韧性截短、还没补的强制位移，记在英雄身上的 buff 名字里（每份模拟各自的，服务器的预演和你看的那场不串）：
/// 到哪个 tick 走完、被截掉几 tick、方向和速度。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Keep {
    pub end: usize,
    pub lost: usize,
    pub dx: i64,
    pub dy: i64,
    pub speed: u64,
}

impl Keep {
    pub fn name(&self) -> String {
        format!("{KEEP}{}:{}:{}:{}:{}", self.end, self.lost, self.dx, self.dy, self.speed)
    }

    pub fn parse(name: &str) -> Option<Keep> {
        let mut it = name.strip_prefix(KEEP)?.split(':');
        let k = Keep {
            end: it.next()?.parse().ok()?,
            lost: it.next()?.parse().ok()?,
            dx: it.next()?.parse().ok()?,
            dy: it.next()?.parse().ok()?,
            speed: it.next()?.parse().ok()?,
        };
        it.next().is_none().then_some(k)
    }

    /// 还是记下的那一下（方向、速度一样）。
    pub fn same(&self, cc: &CcV1) -> bool {
        (self.dx, self.dy, self.speed) == (cc.dx, cc.dy, cc.speed)
    }

    /// 走完了以后补不补：到点才走完（`now` 不早于 `end` 前 2 tick；早停下的是被打断的）、没被按住、不免疫控制。
    pub fn due(&self, now: usize, held: bool, immune: bool) -> bool {
        now + 2 >= self.end && !held && !immune && self.lost > 0
    }
}

/// 一个英雄这一 tick 的样子（[`plan`] 的输入）：韧性、身上记着的 [`Keep`]（和它的 buff 名字）、有没有 [`FULL`]、他的强制位移、
/// 被按住没有、免疫控制没有。
#[derive(Clone, Debug, Default)]
pub struct Seen {
    pub toughness: usize,
    pub keep: Option<(String, Keep)>,
    pub full: bool,
    pub force_move: Option<CcV1>,
    pub held: bool,
    pub immune: bool,
}

/// [`keep_tick`] 对一个英雄做什么。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Plan {
    /// 摘掉的 buff。
    pub remove: Option<String>,
    /// 新记一个 [`Keep`]（buff 时长：走完再多几 tick）。
    pub keep: Option<(Keep, usize)>,
    /// 补上这一截（ForceMove，按他的韧性放长）。
    pub extend: Option<CcV1>,
}

/// 纯逻辑：一个英雄在 `now` 看到的样子 `s` -> 该做什么。
pub fn plan(now: usize, s: &Seen) -> Plan {
    let mut out = Plan::default();
    match (&s.force_move, &s.keep) {
        (Some(c), Some((_, k))) if k.same(c) => {}
        (Some(c), old) => {
            out.remove = old.as_ref().map(|(n, _)| n.clone());
            let seen = c.tick as usize;
            if !s.full && s.toughness > 0 && (1..=MAX_TRACK).contains(&seen) {
                let lost = uncut_ticks(seen, s.toughness) - seen;
                if lost > 0 {
                    out.keep = Some((Keep { end: now + seen, lost, dx: c.dx, dy: c.dy, speed: c.speed }, seen + 4));
                }
            }
        }
        (None, Some((name, k))) => {
            out.remove = Some(name.clone());
            if k.due(now, s.held, s.immune) {
                let mut cc = CcV1::of_kind(CcKindV1::ForceMove, k.lost as u64);
                cc.dx = k.dx;
                cc.dy = k.dy;
                cc.speed = k.speed;
                out.extend = Some(cc);
            }
        }
        (None, None) => {}
    }
    out
}

/// 每 tick（合集的比赛钩子）：每个活着的英雄，被韧性截短、没放长过的强制位移走完以后把截掉的那一截补上（见模块说明）。
pub fn keep_tick(sim: &mut StableSim<'_>) {
    let now = sim.tick();
    let mut todo: Vec<(usize, Plan, usize)> = Vec::new();
    for i in 0..sim.champion_count() {
        let id = sim.champion_id_at(i);
        let Some(u) = sim.get_entity(id) else { continue };
        if !u.is_alive() {
            continue;
        }
        let mut s = Seen::default();
        for k in 0..u.buff_count() {
            let Some(b) = u.buff_at(k) else { continue };
            s.toughness += b.toughness;
            s.immune |= b.cc_immune;
            let n = b.name();
            if n == FULL {
                s.full = true;
            } else if let Some(kp) = Keep::parse(n) {
                s.keep = Some((n.to_string(), kp));
            }
        }
        if s.toughness == 0 && s.keep.is_none() {
            continue;
        }
        s.force_move = (0..u.cc_count()).filter_map(|k| u.cc_at(k)).find(|c| c.kind == CcKindV1::ForceMove.code());
        s.held = held(&u);
        let p = plan(now, &s);
        if p != Plan::default() {
            todo.push((id, p, s.toughness));
        }
    }
    for (id, p, tough) in todo {
        if let Some(name) = &p.remove {
            sim.entity_remove_buff(id, name);
        }
        if let Some((k, ticks)) = p.keep {
            sim.add_buff(id, &BuffV1::timed(&k.name(), ticks));
        }
        if let Some(cc) = p.extend {
            let (lost, speed) = (cc.tick, cc.speed);
            if force_move_full(sim, id, cc) {
                plog(sim, format!("t={now} #{id} KEEP: a forced move cut short by toughness {tough}: +{lost} ticks at {speed} \
                                   (lengthened again for it)"));
            }
        }
    }
}

// ===================== 日志 =====================

/// 一次启动最多记这么多行（服务器的预演也算在里面）。
const LOG_CAP: usize = 400;
static LOG: Mutex<Option<(std::fs::File, usize)>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_push.log");
        }
    }
    PathBuf::from("league_push.log")
}

fn plog(sim: &StableSim<'_>, msg: String) {
    let mut g = LOG.lock().unwrap_or_else(|e| e.into_inner());
    if g.is_none() {
        let path = log_path();
        let _ = std::fs::rename(&path, path.with_extension("prev.log"));
        *g = OpenOptions::new().create(true).append(true).open(&path).ok().map(|f| (f, 0));
    }
    let Some((f, n)) = g.as_mut() else { return };
    if *n >= LOG_CAP {
        return;
    }
    *n += 1;
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        _ => "sim",
    };
    let _ = writeln!(f, "[{kind} m={}] {msg}", o.match_id);
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The engine cuts every crowd control by the target's toughness, x (100 - toughness) / 100, forced moves too:
    /// lengthened by that much a push still goes its whole way, and no further.
    #[test]
    fn a_forced_move_outlasts_the_targets_tenacity() {
        let cut = |ticks: usize, t: usize| ticks * (100 - t) / 100;
        assert_eq!(full_ticks(19, 0), Some(19));
        assert_eq!(full_ticks(19, 30), Some(28));
        assert_eq!(full_ticks(0, 30), Some(0));
        for t in [0, 5, 20, 30, 35, 50, 65, 80, 99] {
            for ticks in 1..=60 {
                let long = full_ticks(ticks, t).unwrap();
                assert!(cut(long, t) >= ticks && cut(long - 1, t) < ticks, "{ticks} ticks, toughness {t}: {long}");
                // what was cut, read back from what is left: never more, and less by under one cut tick's worth
                let back = uncut_ticks(cut(ticks, t), t);
                assert!(back <= ticks && (ticks - back) * (100 - t) < 100, "{ticks} ticks cut to {} at {t}: {back}", cut(ticks, t));
            }
        }
        // from 100 on nothing holds him
        assert_eq!(full_ticks(10, 100), None);
        assert_eq!(full_ticks(10, 130), None);
        assert_eq!(uncut_ticks(7, 100), 7);
    }

    #[test]
    fn held_is_the_hard_crowd_control() {
        let has = |k: CcKindV1| HELD.iter().any(|h| h.code() == k.code());
        for k in [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm] {
            assert!(has(k));
        }
        for k in [CcKindV1::ForceMove, CcKindV1::BlockSkill, CcKindV1::BlockMoveSkill, CcKindV1::Animation] {
            assert!(!has(k));
        }
    }

    #[test]
    fn the_keep_name_reads_back_and_fits_a_buff() {
        let k = Keep { end: 1_234_567, lost: 123, dx: -1_234_567, dy: 7_654_321, speed: 123_456 };
        assert_eq!(Keep::parse(&k.name()), Some(k));
        assert!(k.name().len() <= BUFF_NAME_CAP, "{}", k.name());
        assert_eq!(Keep::parse("push_keep:1:2:3:4"), None);
        assert_eq!(Keep::parse("push_keep:1:2:3:4:5:6"), None);
        assert_eq!(Keep::parse(FULL), None);
    }

    fn fm(tick: u64, dx: i64, speed: u64) -> CcV1 {
        let mut c = CcV1::of_kind(CcKindV1::ForceMove, tick);
        c.dx = dx;
        c.speed = speed;
        c
    }

    /// A knockback cut by tenacity is written down when it shows, kept while it runs, and the cut part pushed once it has
    /// run out - not when another crowd control stopped it early, not for one an add-on lengthened already.
    #[test]
    fn a_move_cut_short_is_finished_once() {
        // first seen: 14 ticks left of 20, toughness 30 -> 6 lost, ends at 1014
        let s = Seen { toughness: 30, force_move: Some(fm(14, 3_000, 2_500)), ..Seen::default() };
        let p = plan(1000, &s);
        let (k, life) = p.keep.expect("written down");
        assert_eq!((k.end, k.lost, k.dx, k.speed, life, p.extend), (1014, 6, 3_000, 2_500, 18, None));
        // still running: nothing
        let running = Seen { toughness: 30, force_move: Some(fm(9, 3_000, 2_500)), keep: Some((k.name(), k)), ..Seen::default() };
        assert_eq!(plan(1005, &running), Plan::default());
        // run out: the cut part, same way and speed
        let over = Seen { toughness: 30, keep: Some((k.name(), k)), ..Seen::default() };
        let p = plan(1014, &over);
        assert_eq!(p.remove, Some(k.name()));
        let c = p.extend.expect("finished");
        assert_eq!((c.tick, c.dx, c.speed), (6, 3_000, 2_500));
        // stopped early (a stun broke it), held, or immune: dropped, not finished
        assert_eq!(plan(1008, &over).extend, None);
        assert_eq!(plan(1014, &Seen { held: true, ..over.clone() }).extend, None);
        assert_eq!(plan(1014, &Seen { immune: true, ..over.clone() }).extend, None);
        // another move took over: the old note goes, the new one is written down
        let other = Seen { toughness: 30, force_move: Some(fm(7, -2_000, 3_000)), keep: Some((k.name(), k)), ..Seen::default() };
        let p = plan(1010, &other);
        assert_eq!(p.remove, Some(k.name()));
        assert_eq!(p.keep.map(|(k, _)| (k.dx, k.lost)), Some((-2_000, 3)));
        // lengthened by an add-on (push_full), no tenacity, or a move with no end: left alone
        assert_eq!(plan(1000, &Seen { full: true, ..s.clone() }), Plan::default());
        assert_eq!(plan(1000, &Seen { toughness: 0, ..s.clone() }), Plan::default());
        assert_eq!(plan(1000, &Seen { force_move: Some(fm(0, 3_000, 2_500)), ..s.clone() }), Plan::default());
    }
}
