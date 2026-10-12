//! 布隆附加包（用户选「主包数据 + 附加包」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的布隆换成 `override/` 里的副本（tools/kit/build_braum.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_braum:heart`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻和 Q 命中英雄时不再走主包「数他自己命中次数」的阶梯，而是调本包的 `league_braum:blow` / `league_braum:bite`；
//! - E 举盾的 buff 不再带减伤，身边友军的减伤 buff 也去掉（本包按方向给）。
//!
//! - **震荡猛击按每个英雄记层**：层数是挂在敌方英雄身上的 buff `league_braum_p_mark`（`entity_stack_buff`，每层 `P_HOLD`
//!   tick、叠一层就全部刷新），第 4 层清掉、眩晕 `P_STUN` tick、造成 `P_DMG` + `P_AP`% 法强魔法伤害，再挂 `P_LOCK` tick 的
//!   `league_braum_p_lockt`：这段时间不再叠层，布隆的普攻额外造成 `P_EXTRA` + `P_EXTRA_AP`% 法强魔法伤害。
//!   **友军普攻也叠层**（英雄联盟原版）：每 tick 读友方英雄的普攻冷却（`cooldowns().0`），跳高了 = 开始一次普攻；离那名友军最近的
//!   敌方单位（小兵、野怪、英雄里最近的，`ALLY_REACH` 以内）如果是带着标记的英雄，就给它叠一层（只有布隆先打上的标记才算数，
//!   和原版一样：第一层必须是布隆的）。
//! - **坚不可摧有方向**：举盾期间盾朝最近的敌方英雄。从前方（盾那一侧的半圆）来的伤害：举盾后第一下全部还回去，之后还回
//!   `e_red`%（受伤后立刻治疗回来）；从背后来的不减。身边 `e_ally_r` 以内、站在他背后（盾的另一侧）的友方英雄每 tick 拿到
//!   2 tick 的 `league_braum_e_ally`（`damaged_reduce` `e_ally`%）：躲在盾后面才有。
//! - **冰川裂隙挑方向**：AI 要放 R 时，把目标换成「从布隆朝它砸过去、线上敌方英雄最多」的那个英雄（`R_RANGE` 以内；
//!   一样多就不换）。
//!
//! 数字：被动的数字写在这里（`P_*`、`R_*`），`tests::the_numbers_match_the_kit` 读主包的参数表核对；E 的参数从英雄数据来。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_braum.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_braum";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";
/// 主包布隆的英雄 id（AI 钩子按它认人）。
const HERO: &str = "league_braum";

// ===================== 数值（主包 build_braum.P） =====================

/// 每层标记持续（p_hold）、眩晕（p_stun）、第 4 层的魔法伤害（p_dmg + p_ap% 法强）、之后不叠层的时间（p_lock）、
/// 这段时间布隆普攻的额外魔法伤害（p_extra + p_extra_ap% 法强）。
pub const P_HOLD: usize = 240;
pub const P_STUN: usize = 60;
pub const P_DMG: usize = 40;
pub const P_AP: usize = 40;
pub const P_LOCK: usize = 480;
pub const P_EXTRA: usize = 12;
pub const P_EXTRA_AP: usize = 10;
/// 友军普攻：离友军这么远以内最近的敌方单位算它打的。
pub const ALLY_REACH: f64 = 75_000.0;
/// 大招：射程（r_range）、裂隙长度（r_len）、宽度（r_w），敌人的身体半径。
pub const R_RANGE: f64 = 75_000.0;
pub const R_LEN: f64 = 80_000.0;
pub const R_W: f64 = 9_000.0;
pub const BODY: f64 = 6_000.0;
/// 举盾时盾朝多远以内最近的敌方英雄。
pub const FACE_REACH: f64 = 90_000.0;

fn br(x: &str) -> String {
    format!("league_braum_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BRAUM_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_braum.log");
        }
    }
    PathBuf::from("league_braum.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 计算（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// `p` 在从 `me` 朝 `dir`（单位向量）的那一侧（前方半圆）吗。
pub fn in_front(me: (f64, f64), dir: (f64, f64), p: (f64, f64)) -> bool {
    (p.0 - me.0) * dir.0 + (p.1 - me.1) * dir.1 > 0.0
}

/// 点 `p` 到线段 `a`-`b` 的距离。
pub fn seg_dist(a: (f64, f64), b: (f64, f64), p: (f64, f64)) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    if len2 <= 0.0 {
        return dist(a, p);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0);
    dist((a.0 + t * dx, a.1 + t * dy), p)
}

/// 从 `me` 朝 `to` 砸出去的裂隙（长 `R_LEN`）上有几个 `champs`。
pub fn on_line(me: (f64, f64), to: (f64, f64), champs: &[(f64, f64)]) -> usize {
    let d = dist(me, to);
    if d <= 0.0 {
        return 0;
    }
    let end = (me.0 + (to.0 - me.0) / d * R_LEN, me.1 + (to.1 - me.1) / d * R_LEN);
    champs.iter().filter(|c| seg_dist(me, end, **c) <= R_W + BODY).count()
}

/// R 的目标：`R_RANGE` 以内、线上英雄最多的那个（`(id, 位置)`）。和 `current` 一样多时留 `current`。
pub fn best_line(me: (f64, f64), champs: &[(usize, (f64, f64))], current: Option<usize>) -> Option<(usize, usize)> {
    let pts: Vec<(f64, f64)> = champs.iter().map(|c| c.1).collect();
    let mut best: Option<(usize, usize)> = None;
    for &(id, at) in champs.iter().filter(|c| dist(me, c.1) <= R_RANGE) {
        let n = on_line(me, at, &pts);
        let better = match best {
            None => true,
            Some((bid, bn)) => n > bn || (n == bn && Some(id) == current && Some(bid) != current),
        };
        if better {
            best = Some((id, n));
        }
    }
    best
}

/// 从前方来的伤害还回去多少：举盾后第一下全部（`first` = 还没挡过），之后 `red`%。
pub fn give_back(damage: usize, first: bool, red: usize) -> usize {
    if first {
        damage
    } else {
        damage * red.min(100) / 100
    }
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn count_buff(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 敌方英雄（活着、能被选中）：(id, 位置)。
fn enemy_champions(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

/// 离 `at` 最近的敌方单位（不算塔），`reach` 以内：(id, 是不是英雄)。
fn nearest_foe(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<(usize, bool)> {
    let mut best: Option<(usize, bool, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let (x, y) = u.pos();
        let d = dist(at, (x as f64, y as f64));
        if d <= reach && best.is_none_or(|b| d < b.2) {
            best = Some((u.id(), u.is_champion(), d));
        }
    }
    best.map(|b| (b.0, b.1))
}

// ===================== 震荡猛击 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Hit {
    /// 布隆的普攻（锁定期间有额外伤害）。
    Attack,
    /// 寒冬之咬。
    Bite,
    /// 友方英雄的普攻（只给已有标记的叠层）。
    Ally(usize),
}

fn magic(sim: &mut StableSim<'_>, braum: usize, target: usize, dmg: usize, ratio: usize) -> usize {
    let ap = sim.get_entity(braum).map_or(0, |e| e.stat().magic_power);
    let amount = dmg + ratio * ap / 100;
    sim.deal_damage_typed(braum, target, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
    amount
}

/// 一下命中：叠层（或锁定期间的额外伤害），第 4 层眩晕。
fn blow(sim: &mut StableSim<'_>, braum: usize, target: usize, hit: Hit) {
    let Some(t) = sim.get_entity(target) else { return };
    if !t.is_alive() || !t.is_champion() {
        return;
    }
    let lock = br("p_lockt");
    let mark = br("p_mark");
    if has_buff(sim, target, &lock) {
        if hit == Hit::Attack {
            let amount = magic(sim, braum, target, P_EXTRA, P_EXTRA_AP);
            sim.play_view_effect(&br("p_extra"), braum, &InputTargetV1::target(target), 0, 0, 0);
            if let Some(n) = counted("extra") {
                wlog(format!("{} EXTRA #{n} {}: +{amount} magic (stunned lately)", head(sim, braum), who(sim, target)));
            }
        }
        return;
    }
    if let Hit::Ally(_) = hit {
        if !has_buff(sim, target, &mark) {
            return;
        }
    }
    let mut stacks = sim.entity_stack_buff(target, &BuffV1::timed(&mark, P_HOLD), 0, true);
    if stacks == 0 {
        // a host without entity_stack_buff: one more copy, refreshed by hand
        let n = count_buff(sim, target, &mark);
        sim.entity_remove_buff(target, &mark);
        for _ in 0..=n {
            sim.add_buff(target, &BuffV1::timed(&mark, P_HOLD));
        }
        stacks = n + 1;
    }
    let by = match hit {
        Hit::Attack => "attack".to_string(),
        Hit::Bite => "Q".to_string(),
        Hit::Ally(a) => format!("ally {}", who(sim, a)),
    };
    if stacks < 4 {
        if let Some(n) = counted("stack") {
            wlog(format!("{} STACK #{n} {} -> {stacks} ({by})", head(sim, braum), who(sim, target)));
        }
        return;
    }
    sim.entity_remove_buff(target, &mark);
    sim.apply_cc(target, &CcV1::stun(P_STUN as u64));
    let amount = magic(sim, braum, target, P_DMG, P_AP);
    sim.add_buff(target, &BuffV1::timed(&lock, P_LOCK));
    sim.add_buff(target, &BuffV1::timed(&br("p_stun"), P_STUN));
    let at = InputTargetV1::target(target);
    sim.play_view_effect(&br("p_proc"), braum, &at, 0, 0, 0);
    sim.play_sfx(&br("p_proc"), braum, &at);
    if let Some(n) = counted("stun") {
        wlog(format!("{} STUN #{n} {}: 4th stack ({by}), {amount} magic, stunned {P_STUN} ticks", head(sim, braum),
                     who(sim, target)));
    }
}

struct Blow;

impl StableEffectType for Blow {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target) {
            blow(sim, caster, input.target_id, Hit::Attack);
        }
    }
}

struct Bite;

impl StableEffectType for Bite {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target) {
            blow(sim, caster, input.target_id, Hit::Bite);
        }
    }
}

// ===================== 被动：友军叠层、坚不可摧的方向 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 举盾时正面伤害还回去的 %（e_red）、背后友军的减伤 %（e_ally）、多远以内的友军（e_ally_r）。
    pub e_red: usize,
    pub e_ally: usize,
    pub e_ally_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { e_red: 40, e_ally: 20, e_ally_r: 25_000 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "e_red" => p.e_red = v,
            "e_ally" => p.e_ally = v,
            "e_ally_r" => p.e_ally_r = v,
            _ => {}
        }
    }
    p
}

/// 每个布隆一份。
#[derive(Clone, Default)]
struct Heart {
    p: Params,
    /// 友方玩家上一 tick 的普攻剩余冷却。
    last: HashMap<usize, usize>,
    /// 举着盾吗、盾朝哪（单位向量）、这次举盾挡过第一下没有、这次举盾挡了多少。
    raised: bool,
    dir: Option<(f64, f64)>,
    blocked_first: bool,
    blocked: usize,
    covered: usize,
}

impl Heart {
    fn ally_attacks(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let mut hits = Vec::new();
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team || c.id() == me {
                continue;
            }
            let Some(cd) = pl.cooldowns() else { continue };
            let was = self.last.insert(pid, cd.0);
            if !c.is_alive() || was.is_none_or(|w| cd.0 <= w + 5) {
                continue;
            }
            let (x, y) = c.pos();
            if let Some((foe, true)) = nearest_foe(sim, team, (x as f64, y as f64), ALLY_REACH) {
                hits.push((c.id(), foe));
            }
        }
        for (ally, foe) in hits {
            blow(sim, me, foe, Hit::Ally(ally));
        }
    }

    fn shield(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let on = has_buff(sim, me, &br("e_on"));
        let Some(at) = alive_at(sim, me) else {
            self.raised = false;
            return;
        };
        if on && !self.raised {
            self.blocked_first = false;
            self.blocked = 0;
            self.covered = 0;
        }
        if !on && self.raised {
            if let Some(n) = counted("raise") {
                wlog(format!("{} SHIELD #{n} down: {} damage given back, {} ally-ticks covered", head(sim, me),
                             self.blocked, self.covered));
            }
        }
        self.raised = on;
        if !on {
            self.dir = None;
            return;
        }
        // the shield faces the nearest enemy champion (he turns it toward the fight)
        let foes = enemy_champions(sim, team);
        if let Some(&(_, f)) = foes.iter().filter(|f| dist(at, f.1) <= FACE_REACH).min_by(|a, b| {
            dist(at, a.1).partial_cmp(&dist(at, b.1)).unwrap_or(std::cmp::Ordering::Equal)
        }) {
            let d = dist(at, f);
            if d > 0.0 {
                self.dir = Some(((f.0 - at.0) / d, (f.1 - at.1) / d));
            }
        }
        let Some(dir) = self.dir else { return };
        let name = br("e_ally");
        let mut behind = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() != team || u.id() == me || !u.is_alive() || !u.is_champion() {
                continue;
            }
            let (x, y) = u.pos();
            let p = (x as f64, y as f64);
            if dist(at, p) <= self.p.e_ally_r as f64 && !in_front(at, dir, p) {
                behind.push(u.id());
            }
        }
        for id in behind {
            sim.entity_remove_buff(id, &name);
            let mut b = BuffV1::timed(&name, 2);
            b.damaged_reduce = self.p.e_ally;
            sim.add_buff(id, &b);
            self.covered += 1;
        }
    }
}

impl StablePassive for Heart {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.last.clear();
        self.raised = false;
        self.dir = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Braum (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.team()) else {
            self.raised = false;
            return;
        };
        self.ally_attacks(sim, me, team);
        self.shield(sim, me, team);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if !self.raised || damage == 0 {
            return;
        }
        let (Some(dir), Some(at), Some(from)) = (self.dir, alive_at(sim, me), alive_at(sim, attacker)) else { return };
        if !in_front(at, dir, from) {
            return;
        }
        let back = give_back(damage, !self.blocked_first, self.p.e_red);
        let first = !self.blocked_first;
        self.blocked_first = true;
        if back == 0 {
            return;
        }
        sim.heal(me, me, back);
        self.blocked += back;
        if let Some(n) = counted("block") {
            wlog(format!("{} BLOCK #{n} {} hit {damage} from the front -> {back} back{}", head(sim, me),
                         who(sim, attacker), if first { " (the first: all)" } else { "" }));
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.last.clear();
        self.raised = false;
        self.dir = None;
    }
}

// ===================== 冰川裂隙挑方向（AI 钩子） =====================

#[derive(Clone, Default)]
struct UltAi;

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        if b.kind != InputKindV1::Ult.code() || InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let (pick, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (x, y) = me.pos();
            let at = (x as f64, y as f64);
            let champs = enemy_champions(&sim, me.team());
            let pts: Vec<(f64, f64)> = champs.iter().map(|c| c.1).collect();
            let was = champs.iter().find(|c| c.0 == current).map_or(0, |c| on_line(at, c.1, &pts));
            let (id, n) = best_line(at, &champs, Some(current))?;
            if id == current || n <= was {
                return None;
            }
            ((id, n, was), format!("{} R {} -> {}", head(&sim, me.id()), who(&sim, current), who(&sim, id)))
        };
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(pick.0));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted("aim") {
            wlog(format!("{line} AIM #{k}: {} champions on the line instead of {}", pick.1, pick.2));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Braum: Concussive Blows per champion with allies' attacks, Unbreakable from the front, Glacial Fissure's line) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:heart"), Heart::default());
    module.add_native_effect(format!("{ID}:blow"), Blow);
    module.add_native_effect(format!("{ID}:bite"), Bite);
    module.add_player_input_ai(UltAi);
    host.log(LogLevel::Info, "league_braum loaded (Concussive Blows per champion, Unbreakable's side, Glacial Fissure's line).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn front_and_back() {
        let me = (0.0, 0.0);
        assert!(in_front(me, (1.0, 0.0), (10.0, 5.0)));
        assert!(!in_front(me, (1.0, 0.0), (-10.0, 5.0)));
        assert!(!in_front(me, (0.0, 1.0), (10.0, -1.0)));
    }

    #[test]
    fn the_first_hit_comes_back_whole() {
        assert_eq!(give_back(200, true, 40), 200);
        assert_eq!(give_back(200, false, 40), 80);
        assert_eq!(give_back(200, false, 140), 200);
    }

    #[test]
    fn the_line_with_most_champions() {
        let me = (0.0, 0.0);
        // a lone champion up, three in a row to the right (the nearest of them 30000 away)
        let champs = [(1, (0.0, 30_000.0)), (2, (30_000.0, 0.0)), (3, (50_000.0, 4_000.0)), (4, (70_000.0, -5_000.0))];
        let (id, n) = best_line(me, &champs, Some(1)).unwrap();
        assert!(matches!(id, 2..=4) && n == 3, "{id} {n}");
        // a tie keeps the AI's own target
        let two = [(1, (0.0, 30_000.0)), (2, (30_000.0, 0.0))];
        assert_eq!(best_line(me, &two, Some(2)).unwrap().0, 2);
        assert_eq!(best_line(me, &two, Some(1)).unwrap().0, 1);
        // out of reach: none
        assert!(best_line(me, &[(5, (90_000.0, 0.0))], None).is_none());
    }

    #[test]
    fn segment_distance() {
        assert!((seg_dist((0.0, 0.0), (10.0, 0.0), (5.0, 3.0)) - 3.0).abs() < 1e-9);
        assert!((seg_dist((0.0, 0.0), (10.0, 0.0), (13.0, 4.0)) - 5.0).abs() < 1e-9);
        assert!((seg_dist((0.0, 0.0), (10.0, 0.0), (-3.0, 4.0)) - 5.0).abs() < 1e-9);
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"ap":40,"dmg":40,"e_ally":20,"e_ally_r":25000,"e_red":40,"extra":12}"#);
        assert_eq!(p, Params { e_red: 40, e_ally: 20, e_ally_r: 25_000 });
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_braum.py");
        let src = std::fs::read_to_string(path).expect("build_braum.py");
        for (key, v) in [("p_hold", P_HOLD), ("p_stun", P_STUN), ("p_dmg", P_DMG), ("p_ap", P_AP), ("p_lock", P_LOCK),
                         ("p_extra", P_EXTRA), ("p_extra_ap", P_EXTRA_AP), ("r_range", R_RANGE as usize),
                         ("r_len", R_LEN as usize), ("r_w", R_W as usize)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_braum.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_mark", "p_lockt", "p_stun", "p_proc", "p_extra", "e_on", "e_ally"] {
            assert!(br(x).len() <= BUFF_NAME_CAP);
        }
    }
}
