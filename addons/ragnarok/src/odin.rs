//! 奥丁（`ragnarok_odin`）数据做不到的部分。数据（tools/kit/build_odin.py）的 `passive` 是这里的 `ragnarok_odin:galdr`，
//! 参数从数据的 `passive.params` 来（build_odin.py 的参数表 P，`NATIVE_KEYS`）。
//!
//! - 第十五呪歌・波命湧出（漫画第 117 话）：生命掉到 `p_hp`% 以下时，冈格尼尔变回项链、光藤缝合伤口：`p_t` 拍里分四下回
//!   `p_heal` + `p_ap`% 法强的生命（真的治疗，飘绿字），冷却 `p_cd` 拍。
//! - 第五呪歌・神環封壁：数据在开盾那一拍给他挂 `ragnarok_odin_e_ward`（`e_t` 拍）。挂着的时候每次挨打都把这一下的血补回去
//!   （挨打前补，补不下的下一拍补），一面盾挡一下，挡满 `e_n` 下 buff 就摘掉；五面盾的循环画面按盾还在不在放
//!   （`WARD_LOOP` 拍一圈）。金时的絶技・金光轟雷斧、掷回来的冈格尼尔会先把这个 buff 摘掉（src/kintoki.rs）。
//! - 第九呪歌・旋影風牙：冈格尼尔打中时目标身上挂着 `ragnarok_odin_q_mark`（数据在伤害前一刻挂上），这一下打之前把它的
//!   护盾清零（无视防御和耐久，一定穿过去）。标记留着：金时靠它认出是冈格尼尔、徒手接住。
//! - 胡金和雾尼：两只渡鸦一直在他身后（`RAVENS_LOOP` 拍放一圈），每条命开始时叫一声。
//! - 配音（速水奨在第三季官方预告里的两句，Codex 截的）：一局第一次和敌方英雄交手、复活时说「夙愿」，开神环封壁、唱心弦融歌时
//!   说「警告」；每类有自己的冷却，任意两句之间至少隔一会儿。
//! - 倒地：死的时候放 Codex 的倒地声（延迟在 sound_info 里）。
//!
//! 经典 SDK 跑不了这里的代码，平衡模拟用 build_odin.py --plain（没有波命湧出和穿盾，五面盾换成护盾）。
//! 日志写在本包的 ragnarok.log 里（行首 `odin`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_odin";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const WARD: &str = "ragnarok_odin_e_ward";
pub const SPEAR_MARK: &str = "ragnarok_odin_q_mark";
/// 双鸦一圈：Codex 的 8 帧 x 0.16 秒
pub const RAVENS_LOOP: usize = 77;
/// 五面盾一圈：8 帧 x 0.11 秒
pub const WARD_LOOP: usize = 53;
/// 波命湧出分几下回
pub const HEAL_PULSES: usize = 4;

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 80;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("odin [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 生命掉到百分之几以下开始唱波命湧出
    pub p_hp: usize,
    /// 波命湧出回多少：固定 + 法强的百分之几
    pub p_heal: usize,
    pub p_ap: usize,
    /// 分几拍回完、冷却几拍
    pub p_t: usize,
    pub p_cd: usize,
    /// 神環封壁：挂几拍（数据给的，这里只记日志）、几面盾
    pub e_t: usize,
    pub e_n: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_hp: 35, p_heal: 120, p_ap: 60, p_t: 120, p_cd: 5400, e_t: 240, e_n: 5 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_hp" => p.p_hp = u.min(100),
            "p_heal" => p.p_heal = u.min(10_000),
            "p_ap" => p.p_ap = u.min(1_000),
            "p_t" => p.p_t = u.clamp(HEAL_PULSES, 6_000),
            "p_cd" => p.p_cd = u.min(36_000),
            "e_t" => p.e_t = u.min(6_000),
            "e_n" => p.e_n = u.clamp(1, 20),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 波命湧出一共回多少。
pub fn heal_total(p: &Params, ap: usize) -> usize {
    p.p_heal + ap * p.p_ap / 100
}

/// 波命湧出第 k 下（从 0 数）回多少：分 HEAL_PULSES 下，余数给最后一下。
pub fn heal_pulse(total: usize, k: usize) -> usize {
    let per = total / HEAL_PULSES;
    if k + 1 == HEAL_PULSES { total - per * (HEAL_PULSES - 1) } else { per }
}

/// 补血：(补完的生命, 补不下的那一截)。
pub fn refund(hp: usize, max: usize, back: usize) -> (usize, usize) {
    let room = max.saturating_sub(hp);
    (hp + back.min(room), back.saturating_sub(room))
}

/// 配音：事件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 复活回来
    Respawn,
    /// 开神環封壁
    Ward,
    /// 唱心弦融歌
    Song,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        Cue::Start | Cue::Respawn => &["v_ambition"],
        Cue::Ward | Cue::Song => &["v_warning"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Respawn => 60 * SECOND,
        Cue::Ward => 30 * SECOND,
        Cue::Song => 40 * SECOND,
    }
}

/// 一份模拟里的配音节奏。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Respawn => "respawn",
            Cue::Ward => "ward",
            Cue::Song => "song",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        let k = Self::key(cue);
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let line = lines_of(cue)[0];
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        if cue == Cue::Start {
            self.started = true;
        }
        Some(line)
    }
}

// ===================== 游戏里 =====================

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 正在唱的波命湧出：下一下在哪一拍、第几下、一共回多少。
#[derive(Clone, Copy, Debug)]
struct Heal {
    next: usize,
    k: usize,
    total: usize,
}

#[derive(Clone, Default)]
struct OdinPassive {
    p: Params,
    me: usize,
    was_alive: bool,
    lives: usize,
    voice: Voice,
    /// 神環封壁还剩几面盾（没开是 None）、下一圈画面在哪一拍
    ward: Option<(usize, usize)>,
    /// 挡下但补不下的血，下一拍补
    owed: usize,
    heal: Option<Heal>,
    heal_ready: usize,
    ravens_next: usize,
    /// Q、E、大招的冷却上一拍是多少，用来认出这一拍刚放了
    cds: (usize, usize, usize),
}

impl OdinPassive {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }

    fn new_life(&mut self, sim: &mut StableSim<'_>, now: usize) {
        self.lives += 1;
        self.ward = None;
        self.owed = 0;
        self.heal = None;
        self.ravens_next = now;
        let me = self.me;
        sim.play_sfx(&vo("p_ravens"), me, &InputTargetV1::target(me));
        if self.lives > 1 {
            self.say(sim, Cue::Respawn);
        }
    }

    /// 五面盾：buff 挂上了就开始数，摘掉了（到时间、挡满、被金时打碎）就停。
    fn tend_ward(&mut self, sim: &mut StableSim<'_>, on: bool, now: usize) {
        let me = self.me;
        match (self.ward, on) {
            (None, true) => {
                self.ward = Some((self.p.e_n, now + WARD_LOOP));
                sim.play_view_effect(&vo("e_ward"), me, &InputTargetV1::target(me), 0, 0, 0);
                log(sim, format!("WARD #{me}: Fafnir up, {} shields", self.p.e_n));
            }
            (Some((left, next)), true) if now >= next => {
                sim.play_view_effect(&vo("e_ward"), me, &InputTargetV1::target(me), 0, 0, 0);
                self.ward = Some((left, now + WARD_LOOP));
            }
            (Some((left, _)), false) => {
                log(sim, format!("WARD #{me}: Fafnir down with {left} shields left"));
                self.ward = None;
            }
            _ => {}
        }
    }

    fn tend_heal(&mut self, sim: &mut StableSim<'_>, hp: usize, max: usize, ap: usize, now: usize) {
        let me = self.me;
        if self.heal.is_none() && now >= self.heal_ready && max > 0 && hp * 100 < max * self.p.p_hp {
            let total = heal_total(&self.p, ap);
            self.heal = Some(Heal { next: now, k: 0, total });
            self.heal_ready = now + self.p.p_cd;
            sim.play_view_effect(&vo("p_heal"), me, &InputTargetV1::target(me), 0, 0, 0);
            sim.play_sfx(&vo("p_heal"), me, &InputTargetV1::target(me));
            log(sim, format!("HEAL #{me}: Idunnar Koppr at {hp}/{max}, {total} over {} ticks", self.p.p_t));
        }
        if let Some(h) = self.heal {
            if now >= h.next {
                sim.heal(me, me, heal_pulse(h.total, h.k));
                self.heal = (h.k + 1 < HEAL_PULSES)
                    .then_some(Heal { next: now + self.p.p_t / HEAL_PULSES, k: h.k + 1, total: h.total });
            }
        }
    }
}

impl StablePassive for OdinPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：这里先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Odin (player {player}, team {team}), {:?}", self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        let now = sim.tick();
        let Some((alive, (hp, max), ap, ward_on)) =
            sim.get_entity(me).map(|e| (e.is_alive(), e.hp(), e.stat().magic_power, has_buff(&e, WARD)))
        else {
            return;
        };
        if alive && !self.was_alive {
            self.new_life(sim, now);
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        if self.owed > 0 {
            let (set, over) = refund(hp, max, self.owed);
            sim.entity_set_hp(me, set);
            self.owed = over.min(max);
        }
        if now >= self.ravens_next {
            sim.play_view_effect(&vo("p_ravens"), me, &InputTargetV1::target(me), 0, 0, 0);
            self.ravens_next = now + RAVENS_LOOP;
        }
        self.tend_ward(sim, ward_on, now);
        let (hp, max) = sim.get_entity(me).map_or((hp, max), |e| e.hp());
        self.tend_heal(sim, hp, max, ap, now);
        // 冷却从 0 跳上去就是刚放了
        let (_, q, e, r) = sim.get_player(player).and_then(|p| p.cooldowns()).unwrap_or((0, 0, 0, 0));
        let (_, e0, r0) = self.cds;
        self.cds = (q, e, r);
        if e > e0 + 30 {
            self.say(sim, Cue::Ward);
        }
        if r > r0 + 30 {
            self.say(sim, Cue::Song);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some((team, champion, marked, shield)) =
            sim.get_entity(target).map(|t| (t.team(), t.is_champion(), has_buff(&t, SPEAR_MARK), t.shield()))
        else {
            return;
        };
        if team == my_team {
            return;
        }
        if champion {
            self.say(sim, Cue::Start);
        }
        // 冈格尼尔：护盾挡不住它（标记留着，金时靠它认出冈格尼尔）
        if marked && shield > 0 {
            let layers = sim.entity_clear_shield(target);
            log(sim, format!("GUNGNIR #{me}: through #{target}'s shield {shield} ({layers} layers)"));
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        self.me = me;
        let Some((left, next)) = self.ward else { return };
        if damage == 0 || left == 0 {
            return;
        }
        // 盾被金时打碎、到了时间：buff 已经没了，这一下照常吃
        let Some((alive, (hp, max), on)) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp(), has_buff(&e, WARD))) else {
            return;
        };
        if !alive || !on {
            return;
        }
        // 这一下在扣血之前：整下补回去（补不下的下一拍补）
        let (set, over) = refund(hp, max, damage);
        sim.entity_set_hp(me, set);
        self.owed += over;
        let left = left - 1;
        sim.play_sfx(&vo("e_block"), me, &InputTargetV1::target(me));
        log(sim, format!("BLOCK #{me}: {damage} from #{attacker}, {left} shields left"));
        if left == 0 {
            sim.entity_remove_buff(me, WARD);
            self.ward = None;
        } else {
            self.ward = Some((left, next));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        self.ward = None;
        self.owed = 0;
        self.heal = None;
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 奥丁的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("odin: {ID} v{VERSION} (Odin: Idunnar Koppr, Fafnir's five shields, Gungnir through shields, the ravens, voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:galdr"), OdinPassive::default());
    host.log(LogLevel::Info, "ragnarok.dll: Odin (Idunnar Koppr, Fafnir, Gungnir, Huginn and Muninn).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_n":5,"e_t":240,"p_ap":60,"p_cd":5400,"p_heal":120,"p_hp":35,"p_t":120}"#;
        assert_eq!(parse_params(json), Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"e_n":0}"#).e_n, 1);
    }

    #[test]
    fn the_heal_adds_up() {
        let p = Params::default();
        assert_eq!(heal_total(&p, 100), 180);
        let total = 181;
        let sum: usize = (0..HEAL_PULSES).map(|k| heal_pulse(total, k)).sum();
        assert_eq!(sum, total);
    }

    #[test]
    fn a_refund_never_passes_max_health() {
        assert_eq!(refund(500, 1000, 200), (700, 0));
        assert_eq!(refund(1000, 1000, 300), (1000, 300));
    }

    #[test]
    fn the_start_line_once_a_match() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_ambition"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Ward, 1000), Some("v_warning"));
        assert_eq!(v.pick(Cue::Song, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Song, 1000 + VOICE_GAP), Some("v_warning"));
        assert_eq!(v.pick(Cue::Ward, 1000 + 30 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Ward, 1000 + 30 * SECOND), Some("v_warning"));
    }

    /// Codex 截的两句都用上。
    #[test]
    fn both_lines_are_used() {
        let mut used: Vec<&str> = [Cue::Start, Cue::Respawn, Cue::Ward, Cue::Song]
            .iter()
            .flat_map(|&c| lines_of(c).iter().copied())
            .collect();
        used.sort();
        used.dedup();
        assert_eq!(used, vec!["v_ambition", "v_warning"]);
    }
}
