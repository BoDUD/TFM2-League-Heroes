//! 开膛手杰克（`ragnarok_jack`）数据做不到的部分：被动「心之色」、Dear GOD 按伤口的扣血、配音、倒地声。数据
//! （tools/kit/build_jack.py）的 `passive` 是这里的 `ragnarok_jack:colour`，参数 p_hp / p_dmg / r_cost 从数据的 params 读；
//! 飞刀、扇形飞刀、神器之伞（伞、后跳）、Dear GOD 的扑击全在数据里。
//!
//! Dear GOD（原作第四回合）：他按住被铁栅栏刺穿的伤口，让血浸透手套——手套碰过的东西都成神器，连血也是。放大招的那一拍
//! （大招冷却从 0 跳上去）扣他 r_cost% 最大生命，最多扣到 1 点（不会自己打死自己）。
//!
//! 心之色（终末的女武神里他看得见人心的颜色）：他打中的是敌方英雄、对方生命低于 p_hp% 时（恐惧藏不住），这一下的伤害
//! +p_dmg%（普攻、技能都算，`on_attack`）。
//!
//! 配音（杉田智和的原声，Codex 截的六句）：一局第一次和敌方英雄交手说一句（表演时间 / 我很期待，偶尔是「接下来请
//! 认识我」），杀了英雄（这就是规矩），放亲爱的神时偶尔「神会染上什么颜色」，复活时（决斗礼节）。每类有自己的冷却，
//! 任意两句之间至少隔一会儿。倒地：死的时候放披风和身子落地（延迟在 sound_info 里）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `jack`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_jack";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("jack #{n} {msg}"));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 对方生命低于百分之几算低血
    pub p_hp: usize,
    /// 打低血的敌方英雄伤害加多少，百分比
    pub p_dmg: usize,
    /// Dear GOD 按伤口扣最大生命的百分之几
    pub r_cost: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_hp: 50,
            p_dmg: 30,
            r_cost: 5,
        }
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
            "p_dmg" => p.p_dmg = u.min(100),
            "r_cost" => p.r_cost = u.min(50),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 对方生命 (现在, 最多) 时，这一下的伤害。
pub fn coloured(damage: usize, hp: (usize, usize), p: &Params) -> usize {
    let (now, max) = hp;
    if max == 0 || now * 100 >= max * p.p_hp {
        return damage;
    }
    damage + damage * p.p_dmg / 100
}

/// 扣完以后的生命：现在 hp、最多 max，扣 cost% 最大生命，最多扣到 1 点（已经只剩 1 点就不扣）。
pub fn after_cost(hp: usize, max: usize, cost: usize) -> usize {
    if hp <= 1 {
        return hp;
    }
    hp.saturating_sub(max * cost / 100).max(1)
}

/// 配音：事件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了亲爱的神
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是「接下来请认识我」（长，偶尔说）
        Cue::Start => &["v_showtime", "v_delight", "v_showtime", "v_delight", "v_reveal"],
        Cue::Kill => &["v_rule"],
        Cue::Ult => &["v_color"],
        Cue::Respawn => &["v_etiquette"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 25 * SECOND,
        // 「神会染上什么颜色」将近十秒，隔久一点
        Cue::Ult => 60 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放大招时喊不喊：冷却到了也只有三成的时候开口
pub const ULT_CHANCE: u64 = 30;

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Kill => "kill",
            Cue::Ult => "ult",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑，别的按顺序轮。
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
        let lines = lines_of(cue);
        let line = if cue == Cue::Start {
            self.started = true;
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

// ===================== 游戏里 =====================

#[derive(Clone, Default)]
struct Colour {
    me: usize,
    p: Params,
    was_alive: bool,
    lives: usize,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl Colour {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(format!("[t={tick}] VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for Colour {
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
        log(format!("[t={}] SPAWN #{me}: ragnarok.dll's Jack (player {player}, team {team}), {:?}", sim.tick(), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
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
        // 大招的冷却从 0 跳上去就是刚放了
        let r_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let ult = r_cd > self.r_cd + 30;
        self.r_cd = r_cd;
        if ult {
            // 按住伤口，血浸透手套
            if let Some((hp, max)) = sim.get_entity(me).map(|e| e.hp()) {
                let after = after_cost(hp, max, self.p.r_cost);
                if after < hp && sim.entity_set_hp(me, after) {
                    log(format!("[t={}] DEAR GOD #{me}: {hp} -> {after} of {max}", sim.tick()));
                }
            }
            if (rng % 100) < ULT_CHANCE {
                self.say(sim, Cue::Ult);
            }
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(hp) = sim.get_entity(target).filter(|t| t.team() != my_team && t.is_champion()).map(|t| t.hp()) else {
            return;
        };
        let before = *damage;
        let out = coloured(before, hp, &self.p);
        if out != before {
            *damage = out;
            log(format!("[t={}] COLOUR #{me} -> #{target} ({}/{} hp): {before} -> {out}", sim.tick(), hp.0, hp.1));
        }
        self.say(sim, Cue::Start);
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

/// 杰克的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("jack: {ID} v{VERSION} (Jack: colours of the heart, Dear GOD's blood, voice lines) registered"));
    module.add_native_passive(format!("{ID}:colour"), Colour::default());
    host.log(LogLevel::Info, "ragnarok.dll: Jack the Ripper (colours of the heart, Dear GOD's blood, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"p_hp": 50, "p_dmg": 30, "r_cost": 5}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params(r#"{"p_hp": 999}"#).p_hp, 100);
        assert_eq!(parse_params(r#"{"r_cost": 99}"#).r_cost, 50);
    }

    #[test]
    fn dear_god_bleeds_but_never_kills_him() {
        assert_eq!(after_cost(1000, 1000, 5), 950);
        assert_eq!(after_cost(30, 1000, 5), 1);
        assert_eq!(after_cost(1, 1000, 5), 1);
    }

    #[test]
    fn only_a_frightened_heart_takes_more() {
        let p = Params::default();
        // 一半以上照常，低于一半加三成
        assert_eq!(coloured(100, (1000, 1000), &p), 100);
        assert_eq!(coloured(100, (500, 1000), &p), 100);
        assert_eq!(coloured(100, (499, 1000), &p), 130);
        assert_eq!(coloured(100, (1, 1000), &p), 130);
        // 拿不到生命（0 / 0）就不动
        assert_eq!(coloured(100, (0, 0), &p), 100);
    }

    #[test]
    fn the_start_line_once_a_match_sometimes_the_long_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_showtime"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 304), Some("v_reveal"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_rule"));
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_color"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_rule"));
    }

    /// Codex 的六句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_six() {
        let six = ["showtime", "delight", "reveal", "rule", "color", "etiquette"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(six.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = six.to_vec();
        all.sort();
        assert_eq!(used, all);
    }
}
