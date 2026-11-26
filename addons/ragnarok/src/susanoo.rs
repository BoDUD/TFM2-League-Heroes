//! 须佐之男命（`ragnarok_susanoo`）数据做不到的部分：无装剑的代价。数据（tools/kit/build_susanoo.py）的 `passive` 是这里的
//! `ragnarok_susanoo:musou`，参数 r_cost 从数据的 params 读；天魔反·无间、天魔反、神罗八百万、无装剑的伤害和控制全在数据里。
//!
//! 无装剑（终末的女武神第十回合）：刀断了以后空手举起看不见的「无之剑」，人用一次就死，他每挥一次都在磨损自己的生命和灵魂，
//! 手和身体开裂。大招放的那一拍（冷却从 0 跳上去）扣他 r_cost% 最大生命，最多扣到 1 点（不会自己打死自己）。
//! 没有配音（官方还没有能确认是他的日语原声，Codex 的交接说明），没有倒地声。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `susanoo`）。

use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_susanoo";
const VERSION: &str = env!("CARGO_PKG_VERSION");

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("susanoo [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 参数和扣血（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 挥一次无装剑扣最大生命的百分之几
    pub r_cost: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_cost: 5 }
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
struct Musou {
    me: usize,
    p: Params,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了
    r_cd: usize,
}

impl StablePassive for Musou {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Susanoo (player {player}, team {team}), {:?}", self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if !alive {
            return;
        }
        // 冷却从 0 跳上去就是刚放了
        let r = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let r0 = self.r_cd;
        self.r_cd = r;
        if r > r0 + 30 {
            let Some((hp, max)) = sim.get_entity(me).map(|e| e.hp()) else { return };
            let after = after_cost(hp, max, self.p.r_cost);
            if after < hp && sim.entity_set_hp(me, after) {
                log(sim, format!("COST #{me}: Musoken {hp} -> {after} of {max}"));
            }
        }
    }
}

// ===================== 注册 =====================

/// 须佐之男的被动（无装剑的代价），注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("susanoo: {ID} v{VERSION} (Susanoo: Musoken's cost) registered"));
    module.add_native_passive(format!("{ID}:musou"), Musou::default());
    host.log(LogLevel::Info, "ragnarok.dll: Susanoo (Musoken's cost).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_cost_never_kills() {
        assert_eq!(after_cost(1000, 1000, 5), 950);
        assert_eq!(after_cost(30, 1000, 5), 1);
        assert_eq!(after_cost(1, 1000, 5), 1);
        assert_eq!(parse_params(r#"{"r_cost": 5}"#), Params::default());
        assert_eq!(parse_params(r#"{"r_cost": 999}"#).r_cost, 50);
    }
}
