//! 阿波罗（`ragnarok_apollo`）数据做不到的部分：被动「白夜的拥抱」和配音。数据（tools/kit/build_apollo.py）的 `passive` 是这里的
//! `ragnarok_apollo:voice`，参数 p_r / p_per / p_max 从数据的 params 读；光辉的支配、阿尔忒弥斯的月影、射穿灵魂的银矢全在数据里。
//!
//! 白夜的拥抱（终末的女武神第九回合：「我这颗太阳不会落下」——身边的人，敌我都算，对他的期待越多他就越强，爆出光）：他打出的每一下
//! （普攻、技能都算，`on_attack`），看他身边 p_r 以内活着的英雄有几个（敌我都算、不算他自己，最多数 p_max 个），每个 +p_per% 伤害。
//!
//! 配音（鈴村健一的官方原声，Codex 截的三句）：一局第一次和敌方英雄交手说选人那句（「你喜欢我吧」），第一次和列奥尼达斯交手
//! （对面有他的话）说「觉得太耀眼吗」那句挑衅；放银箭（射穿灵魂的银矢）时喊；杀了英雄（「觉得太耀眼吗」）；复活时（「你喜欢我吧」）。
//! 每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放 Codex 的着地声（延迟在 sound_info 里，对上死亡动作第 7 帧着地）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `apollo`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_apollo";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 宿敌：第九回合的对手
const RIVAL: &str = "ragnarok_leonidas";

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("apollo [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 一局里第一次和列奥尼达斯交手
    Rival,
    /// 放了银箭突进
    Ult,
    /// 杀了敌方英雄
    Kill,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        Cue::Start => &["v_select"],
        Cue::Rival => &["v_challenge"],
        Cue::Ult => &["v_silver_arrow"],
        Cue::Kill => &["v_challenge"],
        Cue::Respawn => &["v_select"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start | Cue::Rival => usize::MAX,
        Cue::Ult => 40 * SECOND,
        Cue::Kill => 25 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    once: Vec<&'static str>,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Rival => "rival",
            Cue::Ult => "ult",
            Cue::Kill => "kill",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那两句一局各说一次，开场那句按拍数挑（同一局的几份模拟挑的
    /// 一样），别的按顺序轮。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        let k = Self::key(cue);
        let once = matches!(cue, Cue::Start | Cue::Rival);
        if once && self.once.contains(&k) {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let lines = lines_of(cue);
        let line = if once {
            self.once.push(k);
            lines[tick % lines.len()]
        } else {
            let turn = self.turn.entry(k).or_insert(0);
            *turn += 1;
            lines[(*turn - 1) % lines.len()]
        };
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(line)
    }
}

// ===================== 白夜的拥抱（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 数多远以内的英雄（游戏单位，1 个游戏像素 1000）
    pub p_r: usize,
    /// 每个英雄加百分之几的伤害
    pub p_per: usize,
    /// 最多数几个
    pub p_max: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_r: 50000, p_per: 6, p_max: 5 }
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
            "p_r" => p.p_r = u.min(200000),
            "p_per" => p.p_per = u.min(50),
            "p_max" => p.p_max = u.min(9),
            _ => {}
        }
    }
    p
}

/// 身边有 n 个英雄时这一下的伤害。
pub fn embraced(damage: usize, n: usize, p: &Params) -> usize {
    damage * (100 + n.min(p.p_max) * p.p_per) / 100
}

/// 他身边 p_r 以内活着的英雄（敌我都算，不算他自己）有几个。
fn watchers(sim: &StableSim<'_>, me: usize, p: &Params) -> usize {
    let Some((mx, my)) = sim.get_entity(me).map(|e| e.pos()) else { return 0 };
    let r2 = (p.p_r as f64) * (p.p_r as f64);
    let mut n = 0;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.id() == me || !u.is_alive() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        let (dx, dy) = (x as f64 - mx as f64, y as f64 - my as f64);
        if dx * dx + dy * dy <= r2 {
            n += 1;
        }
    }
    n
}

// ===================== 游戏里 =====================

#[derive(Clone, Default)]
struct ApolloVoice {
    me: usize,
    p: Params,
    was_alive: bool,
    lives: usize,
    /// 银箭突进的冷却上一拍是多少，用来认出这一拍刚放了
    ult_cd: usize,
    voice: Voice,
}

impl ApolloVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for ApolloVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Apollo (player {player}, team {team})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        // 冷却从 0 跳上去就是刚放了
        let r = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let r0 = self.ult_cd;
        self.ult_cd = r;
        if r > r0 + 30 {
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(t) = sim.get_entity(target) else { return };
        if t.team() == my_team {
            return;
        }
        // 白夜的拥抱：身边的英雄越多越强
        let n = watchers(sim, me, &self.p);
        if n > 0 {
            *damage = embraced(*damage, n, &self.p);
        }
        if !t.is_champion() {
            return;
        }
        if t.name().as_deref() == Some(RIVAL) {
            self.say(sim, Cue::Rival);
        } else {
            self.say(sim, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 阿波罗的被动（只有声音），注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("apollo: {ID} v{VERSION} (Apollo: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), ApolloVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Apollo (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_select"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
    }

    #[test]
    fn the_rival_line_once_a_match_apart_from_the_start_line() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Rival, 300), Some("v_challenge"));
        // 和列奥尼达斯交手过了，第一次打别的英雄还会说开场那句（隔够了就行）
        assert_eq!(v.pick(Cue::Start, 300 + VOICE_GAP), Some("v_select"));
        assert_eq!(v.pick(Cue::Rival, 300 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_challenge"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_silver_arrow"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_challenge"));
        // 大招那句隔 40 秒，复活那句隔一分钟
        let mut z = Voice::default();
        assert_eq!(z.pick(Cue::Ult, 0), Some("v_silver_arrow"));
        assert_eq!(z.pick(Cue::Ult, 40 * SECOND - 1), None);
        assert_eq!(z.pick(Cue::Ult, 40 * SECOND), Some("v_silver_arrow"));
        let mut d = Voice::default();
        assert_eq!(d.pick(Cue::Respawn, 0), Some("v_select"));
        assert_eq!(d.pick(Cue::Respawn, 60 * SECOND - 1), None);
    }

    /// Codex 的三句都用上。
    #[test]
    fn every_line_is_one_of_codexs_three() {
        let three = ["select", "challenge", "silver_arrow"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Rival, Cue::Ult, Cue::Kill, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(three.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = three.to_vec();
        all.sort();
        assert_eq!(used, all);
    }

    #[test]
    fn the_more_who_watch_the_brighter_he_burns() {
        let p = Params::default();
        assert_eq!(parse_params(r#"{"p_max": 5, "p_per": 6, "p_r": 50000}"#), p);
        assert_eq!(embraced(1000, 0, &p), 1000);
        assert_eq!(embraced(1000, 2, &p), 1120);
        // 最多数 5 个
        assert_eq!(embraced(1000, 9, &p), 1300);
    }
}
