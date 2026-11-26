//! 别西卜（`ragnarok_beelzebub`）数据做不到的部分：配音和虚神的反噬。数据（tools/kit/build_beelzebub.py）的 `passive` 是这里的
//! `ragnarok_beelzebub:voice`，参数 r_cost 从数据的 params 读；恶魔的振翅（被动）、暴食的堕天使、地狱之门扉、虚神（卡俄斯）的
//! 伤害和控制全在数据里。
//!
//! 虚神的反噬（终末的女武神第八回合：「冥界的原罪·零号：虚神」对敌人致命，他自己也重伤，哈迪斯禁止他用）：大招放的那一拍
//! （冷却从 0 跳上去）扣他 r_cost% 最大生命，最多扣到 1 点（不会自己打死自己）。
//!
//! 配音（浪川大辅的官方原声，Codex 截的五句）：一局第一次和敌方英雄交手说一句（「这倒有意思」，五次里一次是长的迎战宣言），
//! 第一次和特斯拉交手（对面有他的话）说催促对手那句；放地狱之门时一半的时候喊招式；杀了英雄（结局的独白）；复活时（迎战宣言）。
//! 每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放 Codex 的骸骨杖落地声和着地声（延迟在 sound_info 里，对上死亡
//! 动作第 5 帧杖落地、第 7 帧着地）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `beelzebub`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_beelzebub";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 宿敌：第八回合的对手
const RIVAL: &str = "ragnarok_tesla";

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
        crate::wlog(format!("beelzebub [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 一局里第一次和特斯拉交手
    Rival,
    /// 放了地狱之门
    Guard,
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
        // 五份里一份是长的迎战宣言
        Cue::Start => &["v_interest", "v_interest", "v_oath", "v_interest", "v_interest"],
        Cue::Rival => &["v_taunt"],
        Cue::Guard => &["v_guard"],
        Cue::Kill => &["v_win"],
        Cue::Respawn => &["v_oath"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start | Cue::Rival => usize::MAX,
        Cue::Guard => 30 * SECOND,
        Cue::Kill => 25 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放地狱之门时喊不喊：冷却到了也只有一半的时候开口
pub const SKILL_CHANCE: u64 = 50;

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
            Cue::Guard => "guard",
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

// ===================== 虚神的反噬（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 放一次虚神扣最大生命的百分之几
    pub r_cost: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_cost: 6 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        if k == "r_cost" {
            p.r_cost = (v.max(0) as usize).min(50);
        }
    }
    p
}

/// 扣完以后的生命：现在 hp、最多 max，扣 cost% 最大生命，最多扣到 1 点（已经只剩 1 点就不扣）。
pub fn after_cost(hp: usize, max: usize, cost: usize) -> usize {
    if hp <= 1 {
        return hp;
    }
    hp.saturating_sub(max * cost / 100).max(1)
}

// ===================== 游戏里 =====================

#[derive(Clone, Default)]
struct BeelzebubVoice {
    me: usize,
    p: Params,
    was_alive: bool,
    lives: usize,
    /// 地狱之门扉、虚神的冷却上一拍是多少，用来认出这一拍刚放了
    e_cd: usize,
    r_cd: usize,
    voice: Voice,
}

impl BeelzebubVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for BeelzebubVoice {
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
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Beelzebub (player {player}, team {team})"));
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
        // 冷却从 0 跳上去就是刚放了
        let (_, _, e, r) = sim.get_player(player).and_then(|p| p.cooldowns()).unwrap_or((0, 0, 0, 0));
        let e0 = self.e_cd;
        self.e_cd = e;
        if e > e0 + 30 && (rng % 100) < SKILL_CHANCE {
            self.say(sim, Cue::Guard);
        }
        let r0 = self.r_cd;
        self.r_cd = r;
        if r > r0 + 30 {
            // 虚神的反噬
            let Some((hp, max)) = sim.get_entity(me).map(|x| x.hp()) else { return };
            let after = after_cost(hp, max, self.p.r_cost);
            if after < hp && sim.entity_set_hp(me, after) {
                log(sim, format!("COST #{me}: Chaos {hp} -> {after} of {max}"));
            }
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(t) = sim.get_entity(target) else { return };
        if t.team() == my_team || !t.is_champion() {
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

/// 别西卜的被动（只有声音），注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("beelzebub: {ID} v{VERSION} (Beelzebub: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), BeelzebubVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Beelzebub (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match_sometimes_the_long_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_interest"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 302), Some("v_oath"));
    }

    #[test]
    fn the_rival_line_once_a_match_apart_from_the_start_line() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Rival, 300), Some("v_taunt"));
        // 和特斯拉交手过了，第一次打别的英雄还会说开场那句（隔够了就行）
        assert_eq!(v.pick(Cue::Start, 300 + VOICE_GAP), Some("v_interest"));
        assert_eq!(v.pick(Cue::Rival, 300 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_win"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Guard, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Guard, 1000 + VOICE_GAP), Some("v_guard"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_win"));
        // 地狱之门那句隔 30 秒
        let mut g = Voice::default();
        assert_eq!(g.pick(Cue::Guard, 0), Some("v_guard"));
        assert_eq!(g.pick(Cue::Guard, 30 * SECOND - 1), None);
        assert_eq!(g.pick(Cue::Guard, 30 * SECOND), Some("v_guard"));
    }

    /// Codex 的五句都用上。
    #[test]
    fn every_line_is_one_of_codexs_five() {
        let five = ["interest", "taunt", "guard", "oath", "win"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Rival, Cue::Guard, Cue::Kill, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(five.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = five.to_vec();
        all.sort();
        assert_eq!(used, all);
    }

    #[test]
    fn chaos_hurts_him_but_never_kills() {
        assert_eq!(after_cost(1000, 1000, 6), 940);
        assert_eq!(after_cost(40, 1000, 6), 1);
        assert_eq!(after_cost(1, 1000, 6), 1);
        assert_eq!(parse_params(r#"{"r_cost": 6}"#), Params::default());
    }
}
