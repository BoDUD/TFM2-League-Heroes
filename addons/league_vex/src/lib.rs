//! 薇古丝附加包：照英雄联盟的规则做主包数据做不到的三件事（用户 2026-10-20：技能方案 A，做附加包）。
//!
//! 主包保持纯数据：数据只能读她自己身上的 buff，读不到敌人身上的暮气，所以主包里溟濛渐染打中英雄后，她下一次技能打中英雄就补暮气伤害
//! （不管那个人身上有没有暮气）；读不到别人在突进；也刷新不了大招。`mod.override_info` 把主包的薇古丝换成 `override/` 里的副本
//! （`tools/kit/build_vex.py --native`），被动 `league_vex:gloom`：
//!
//! - **暮气**：溟濛渐染打中的敌人身上挂 `league_vex_g_mark`（`g_t` tick，主包也挂）；另外**她身边 `p_dash_r` 以内突进的敌方英雄**
//!   （一 tick 里移动了至少 `DASH_STEP`、不到 `BLINK_MAX`：闪现、传送不算）也被挂上。副本里她的每一下伤害（普攻、Q、W、R 的飞弹和
//!   冲击，E 不算）给打中的单位挂 2 tick 的 `league_vex_v_hit`；带暮气的单位被她打中就**引爆**：摘掉暮气，补 `g_dmg` + `g_ratio`%
//!   法强魔法伤害（`g_pop` 的画面和声音），**终焉的等待缩短 `g_cut`%**（她身上的 `league_vex_p_wait` 剩下的时间）。
//! - **终焉回来**：副本里不再用数据的延时放「终焉好了」的画面（等待会被缩短）；本包看 `p_wait` 消失时放 `p_ready` 的画面和声音。
//! - **愁煞刷新**：愁煞的飞弹打中的英雄挂 `league_vex_r_mark`；他在 `r_reset` tick 内死了（谁杀的都算，英雄联盟：被愁煞伤害后 6 秒内
//!   阵亡）就把她的大招冷却清零。
//!
//! 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）：引爆补的伤害不挂
//! `v_hit`，不会再引爆一次。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个薇古丝自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vex.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `GLOOM`（引爆）、`DASH`（突进挂暮气）、`DOOM`（终焉好了）、`RESET`（大招刷新）、`WATCH`（每 30 秒的计数），都限了条数。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_vex";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";
/// 一 tick 里至少走这么远算突进（走路约 1000，加速后 1500；冲刺 2500 起，league_poppy 量的），超过这么远算闪现 / 传送。
pub const DASH_STEP: f64 = 2_200.0;
pub const BLINK_MAX: f64 = 20_000.0;
/// 冷却清零时一次减掉的 tick（比任何大招的冷却都长）。
const RESET_TICKS: usize = 100_000;

/// 主包薇古丝的名字（buff、声音、画面都以它开头）。
fn vx(x: &str) -> String {
    format!("league_vex_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VEX_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vex.log");
        }
    }
    PathBuf::from("league_vex.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 终焉的等待（tick）。
    pub p_cd: usize,
    /// 突进的敌方英雄离她多近会被挂上暮气。
    pub p_dash_r: usize,
    /// 暮气：持续 tick，引爆伤害（固定值、法强 %），每次引爆缩短终焉等待的 %。
    pub g_t: usize,
    pub g_dmg: usize,
    pub g_ratio: usize,
    pub g_cut: usize,
    /// 愁煞打中后多少 tick 内阵亡就刷新大招。
    pub r_reset: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_cd: 900, p_dash_r: 60000, g_t: 360, g_dmg: 40, g_ratio: 20, g_cut: 25, r_reset: 360 }
    }
}

/// `{"g_dmg":40,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "p_cd" => &mut p.p_cd,
            "p_dash_r" => &mut p.p_dash_r,
            "g_t" => &mut p.g_t,
            "g_dmg" => &mut p.g_dmg,
            "g_ratio" => &mut p.g_ratio,
            "g_cut" => &mut p.g_cut,
            "r_reset" => &mut p.r_reset,
            _ => continue,
        };
        *slot = v;
    }
    p.g_cut = p.g_cut.min(100);
    p
}

// ===================== 计算 =====================

/// 引爆暮气的魔法伤害（减免前）。
pub fn gloom_damage(p: &Params, ap: usize) -> usize {
    p.g_dmg + p.g_ratio * ap / 100
}

/// 终焉还要等 `left` tick 时引爆一次后还要等多久。
pub fn doom_after_cut(p: &Params, left: usize) -> usize {
    left * (100 - p.g_cut) / 100
}

/// 一 tick 走了 `step` 算不算突进（闪现、传送那么远的不算）。
pub fn is_dash(step: f64) -> bool {
    (DASH_STEP..=BLINK_MAX).contains(&step)
}

fn dist(a: (u64, u64), b: (u64, u64)) -> f64 {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    (dx * dx + dy * dy).sqrt()
}

// ===================== 被动 =====================

/// 每个薇古丝一份。
#[derive(Clone, Default)]
struct Gloom {
    p: Params,
    /// 上一 tick 身上有暮气的单位。
    gloomed: Vec<usize>,
    /// 上一 tick 身上有她的打中标记的单位（一下只引爆一次）。
    hit_seen: Vec<usize>,
    /// 每个敌方英雄上一 tick 的位置。
    last_pos: Vec<(usize, (u64, u64))>,
    /// 上一 tick 她身上有终焉的等待。
    waiting: bool,
    /// 愁煞打中的英雄和刷新的截止 tick。
    marked: Vec<(usize, usize)>,
    r_seen: Vec<usize>,
    pops: usize,
    dashes: usize,
    dooms: usize,
    resets: usize,
    next_report: usize,
}

fn buff_of(sim: &StableSim<'_>, id: usize, name: &str) -> Option<BuffV1> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == name)
}

impl Gloom {
    /// 暮气：她打中带暮气的单位就引爆。
    fn detonate(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize) {
        let (g, h) = (vx("g_mark"), vx("v_hit"));
        let mut gloomed = Vec::new();
        let mut hit = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            let names: Vec<String> = (0..e.buff_count()).filter_map(|k| e.buff_at(k)).map(|b| b.name().to_string()).collect();
            if names.iter().any(|n| *n == g) {
                gloomed.push(e.id());
            }
            if names.iter().any(|n| *n == h) {
                hit.push(e.id());
            }
        }
        let mut popped = Vec::new();
        for &id in &hit {
            // a mark laid this very tick (E lands and the add-on sees it with her hit) waits for the next hit
            if self.hit_seen.contains(&id) || !gloomed.contains(&id) || !self.gloomed.contains(&id) {
                continue;
            }
            sim.entity_remove_buff(id, &vx("g_mark"));
            let dmg = gloom_damage(&self.p, ap);
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let at = InputTargetV1::target(id);
            sim.play_view_effect(&vx("g_pop"), me, &at, 0, 0, 0);
            sim.play_sfx(&vx("g_pop"), me, &at);
            popped.push(id);
            self.pops += 1;
            // Doom's wait shortened
            let mut left = None;
            if let Some(b) = buff_of(sim, me, &vx("p_wait")) {
                let rest = doom_after_cut(&self.p, b.duration_tick);
                sim.entity_remove_buff(me, &vx("p_wait"));
                if rest > 0 {
                    sim.add_buff(me, &BuffV1::timed(&vx("p_wait"), rest));
                }
                left = Some((b.duration_tick, rest));
            }
            if self.pops <= 10 || self.pops % 25 == 0 {
                wlog(format!("{} GLOOM #{}: #{id} popped for {dmg} magic; Doom wait {left:?}", head(sim, me), self.pops));
            }
        }
        self.gloomed = gloomed.into_iter().filter(|id| !popped.contains(id)).collect();
        self.hit_seen = hit;
    }

    /// 她身边突进的敌方英雄挂上暮气。
    fn dashes(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), alive: bool) {
        let mut now = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            let at = e.pos();
            now.push((id, at));
            let Some(&(_, was)) = self.last_pos.iter().find(|x| x.0 == id) else { continue };
            if !alive || dist(pos, at) > self.p.p_dash_r as f64 || !is_dash(dist(was, at)) {
                continue;
            }
            if buff_of(sim, id, &vx("g_mark")).is_some() {
                sim.entity_remove_buff(id, &vx("g_mark"));
            } else {
                self.dashes += 1;
                if self.dashes <= 10 || self.dashes % 25 == 0 {
                    wlog(format!("{} DASH #{}: #{id} dashed {:.0} within {:.0} of her -> Gloom", head(sim, me),
                                 self.dashes, dist(was, at), dist(pos, at)));
                }
                sim.play_sfx(&vx("e_hit"), me, &InputTargetV1::target(id));
            }
            sim.add_buff(id, &BuffV1::timed(&vx("g_mark"), self.p.g_t));
        }
        self.last_pos = now;
    }

    /// 终焉的等待结束：放「终焉好了」。
    fn doom(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        let waiting = buff_of(sim, me, &vx("p_wait")).is_some();
        if self.waiting && !waiting && alive {
            let at = InputTargetV1::target(me);
            sim.play_view_effect(&vx("p_ready"), me, &at, 0, 0, 0);
            sim.play_sfx(&vx("p_ready"), me, &at);
            self.dooms += 1;
            if self.dooms <= 6 {
                wlog(format!("{} DOOM #{}: ready", head(sim, me), self.dooms));
            }
        }
        self.waiting = waiting;
    }

    /// 愁煞：打中的英雄在 `r_reset` tick 内死了就刷新大招。
    fn surge(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize) {
        let mark = vx("r_mark");
        let mut seen = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            if (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == mark) {
                seen.push(id);
                if !self.r_seen.contains(&id) {
                    self.marked.retain(|m| m.0 != id);
                    self.marked.push((id, tick + self.p.r_reset));
                }
            }
        }
        self.r_seen = seen;
        let mut keep = Vec::new();
        for (id, until) in std::mem::take(&mut self.marked) {
            if tick > until {
                continue;
            }
            if sim.get_entity(id).map_or(true, |e| e.is_alive()) {
                keep.push((id, until));
                continue;
            }
            let cd = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
            sim.entity_reduce_cooldown(me, SkillSlotV1::Ult, RESET_TICKS);
            self.resets += 1;
            wlog(format!("{} RESET #{}: #{id} died {} ticks before the mark ran out -> ult cooldown {cd} -> 0",
                         head(sim, me), self.resets, until - tick));
        }
        self.marked = keep;
    }
}

impl StablePassive for Gloom {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        self.last_pos.clear();
        wlog(format!("{} SPAWN: the add-on's Vex (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ap = e.stat().magic_power;
        let pos = e.pos();
        let alive = e.is_alive();
        let tick = sim.tick();
        // Gloom pops and the reset go on after her death (her missile still flying); only a living Vex marks a dash
        self.detonate(sim, me, team, ap);
        self.dashes(sim, me, team, pos, alive);
        self.doom(sim, me, alive);
        self.surge(sim, me, team, tick);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: Gloom pops {}, dashes marked {}, Doom ready {}, ult resets {}", head(sim, me),
                             self.pops, self.dashes, self.dooms, self.resets));
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Vex's Gloom on each enemy, dashes marked, Shadow Surge reset) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:gloom"), Gloom::default());
    host.log(LogLevel::Info, "league_vex v1 loaded (Vex's Gloom on each enemy, dashes marked, Shadow Surge reset).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"g_dmg":50,"g_cut":30,"r_reset":300,"x":1}"#);
        assert_eq!((p.g_dmg, p.g_cut, p.r_reset), (50, 30, 300));
        assert_eq!(p.g_ratio, Params::default().g_ratio);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"g_cut":150}"#).g_cut, 100);
    }

    #[test]
    fn a_pop_deals_its_damage_and_shortens_doom() {
        let p = Params::default();
        assert_eq!(gloom_damage(&p, 100), 60); // 40 + 20 % of 100 AP
        assert_eq!(doom_after_cut(&p, 800), 600);
        assert_eq!(doom_after_cut(&p, 0), 0);
        assert_eq!(doom_after_cut(&parse_params(r#"{"g_cut":100}"#), 800), 0);
    }

    #[test]
    fn a_dash_is_faster_than_walking_and_shorter_than_a_blink() {
        assert!(!is_dash(1_000.0));
        assert!(!is_dash(1_500.0));
        assert!(is_dash(2_500.0));
        assert!(is_dash(6_000.0));
        assert!(!is_dash(50_000.0));
    }

    #[test]
    fn buff_names_fit() {
        for x in ["g_mark", "v_hit", "g_pop", "p_wait", "p_ready", "r_mark", "e_hit"] {
            assert!(vx(x).len() <= BUFF_NAME_CAP);
        }
    }
}
