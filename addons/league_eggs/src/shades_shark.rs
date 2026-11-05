//! 6 太阳镜防晒、9 鲨鱼吃小矮子：数据那一半在主包（agent B，2026-11-05），这里是比赛钩子这一半（agent B 的代码，按本包的每份
//! 模拟一份状态、日志写法接上）。
//!
//! 6 太阳镜防晒：主包莱昂娜的「烈阳」不是英雄联盟的引爆，她的 Q、E、W、R 打中的每个敌人挂一层 `league_leona_sunlight`
//! （damaged_amplify 10、90 tick；每打中一次多一层，加伤叠加）。数据读不到被打的是谁（SwitchByBuff 只读施法者），所以由钩子做：
//! 戴墨镜的英雄身上有 n 层烈阳，就让他也有 n 层 `league_leona_shades`（每层 damaged_reduce 1、2 tick、每 tick 续上）。
//! damaged_amplify 和 damaged_reduce 先相加再乘（league_darius_ult 的 plan.rs，经典 SDK 量过：减 50 + 加 50 = 原伤害），
//! 所以戴墨镜的人每层烈阳多受 9% 而不是 10%：「少 1 点」。画面（莱昂娜身边的一副墨镜）在主包莱昂娜的 view_buffs 里。
//!
//! 9 鲨鱼吃小矮子：菲兹的鲨鱼每一口（R 的三条鲨鱼和没中鱼时的大鲨鱼）先给咬到的每个敌人挂 2 tick 的 `league_fizz_r_eat`
//! （在这一口的伤害之前）；被这一口咬死的单位身上的标记跟着尸体冻住（死去的单位的 buff 停在死的那一刻，league_riven 的 R
//! 在游戏里看过）。身上有标记的小约德尔人的尸体在死后 `GULP_AFTER` tick（鲨鱼的画面那时潜回水里）被吞掉：放逐 `GULP_T` tick，
//! 锁定画面是菲兹的 `league_fizz_r_gulp`（水面合上、冒泡，0.58 秒，然后空帧）。被放逐的单位画成它的锁定画面而不是它自己
//! （league_karthus 的灵体、league_zaahen 的复活）；客户端会不会也藏起死掉的被放逐的尸体，要等游戏里看（`EATEN` 一行写了宿主
//! 收没收这个放逐）。

use mod_api_stable::*;

// `super`, not `crate`: in the league_addons bundle this file is a module of a module
use super::rules::{Hero, SUNGLASSES, SWALLOWED};
use super::{head, say};

// ===================== 6 太阳镜防晒 =====================

pub const SUNLIGHT: &str = "league_leona_sunlight";
pub const SHADES: &str = "league_leona_shades";
pub const SHADES_T: usize = 2;

/// 画上戴墨镜 / 护目镜遮住眼睛的英雄（加上李青的蒙眼布，用户自己举的例子）：`rules::SUNGLASSES`。
pub fn wears_sunglasses(champion: &str) -> bool {
    Hero::of(champion).is_some_and(|h| SUNGLASSES.contains(&h))
}

/// 一个戴墨镜的人身上 `sun` 层烈阳、`shades` 层墨镜：(先把墨镜全摘掉, 挂几层, 续上身上的)。
pub fn shades_step(sun: usize, shades: usize) -> (bool, usize, bool) {
    if sun == shades {
        (false, 0, sun > 0)
    } else {
        (shades > 0, sun, false)
    }
}

pub fn shade_buff() -> BuffV1 {
    let mut b = BuffV1::timed(SHADES, SHADES_T);
    b.damaged_reduce = 1;
    b
}

/// (烈阳, 墨镜) 的层数。
fn layers(sim: &StableSim<'_>, id: usize) -> (usize, usize) {
    let Some(e) = sim.get_entity(id) else { return (0, 0) };
    let (mut sun, mut shades) = (0, 0);
    for b in (0..e.buff_count()).filter_map(|j| e.buff_at(j)) {
        if b.name() == SUNLIGHT {
            sun += 1;
        } else if b.name() == SHADES {
            shades += 1;
        }
    }
    (sun, shades)
}

/// 每 tick：`wearers`（对面有莱昂娜的戴墨镜的玩家）里每个活着的，身上每层烈阳配一层墨镜。-> 这一 tick 新挂上的墨镜层数。
pub fn shades_tick(sim: &mut StableSim<'_>, wearers: &[usize], screen: bool) -> usize {
    let mut put = 0;
    for &p in wearers {
        let Some(e) = sim.get_player(p).and_then(|x| x.champion()) else { continue };
        if !e.is_alive() {
            continue;
        }
        let (id, name) = (e.id(), e.name().unwrap_or_default());
        let (sun, shades) = layers(sim, id);
        let (clear, add, refresh) = shades_step(sun, shades);
        if clear {
            sim.entity_remove_buff(id, SHADES);
        }
        for _ in 0..add {
            sim.add_buff(id, &shade_buff());
        }
        if refresh {
            sim.entity_stack_buff(id, &shade_buff(), sun, true);
        }
        if add > shades {
            let got = layers(sim, id).1;
            put += got.saturating_sub(shades);
            if got < sun {
                say(screen, "shades refused", format!("{} SHADES REFUSED {name}#{id}: Leona's Sunlight x{sun}, shades x{got} \
                                                       after adding {add}", head(sim)));
            } else {
                say(screen, "shades", format!("{} SHADES {name}#{id}: Leona's Sunlight x{sun} -> shades x{got} (+{}% damage \
                                               taken, not +{}%)", head(sim), 9 * sun, 10 * sun));
            }
        }
    }
    put
}

// ===================== 9 鲨鱼吃小矮子 =====================

pub const FIZZ: &str = "league_fizz";
pub const EAT: &str = "league_fizz_r_eat";
pub const GULP: &str = "league_fizz_r_gulp";
/// 鲨鱼的画面（league_fizz_big 的 r_shark1-3：8 帧 x 70 ms）第 2-3 帧咬、第 4 帧潜下去。
pub const GULP_AFTER: usize = 15;
/// 比任何复活都长：英雄复活是新的实体，死掉的那个和它的放逐一起消失（league_sion 11-03 的日志）。要是游戏哪天让同一个实体
/// 活过来，`Shark::tick` 在它活过来的那一 tick 就解除放逐。
pub const GULP_T: usize = 7_200;

/// 鲨鱼吞得下的小约德尔人（`rules::SWALLOWED`：提莫太重、黑默丁格头太大，不吞），死了、身上有鲨鱼咬的标记。
pub fn swallows(champion: &str, alive: bool, marked: bool) -> bool {
    !alive && marked && Hero::of(champion).is_some_and(|h| SWALLOWED.contains(&h))
}

/// 一份模拟一个（在 `Sim` 里，按 SIM_TAG 的编号记）。
#[derive(Clone, Debug, Default)]
pub struct Shark {
    /// (尸体, 吞掉的那一 tick)
    due: Vec<(usize, usize)>,
    /// 看过的尸体（吞了、排着要吞、或者不是被鲨鱼咬死的小约德尔人）：每具只看一次，活过来、没了就忘掉
    seen: Vec<usize>,
    /// 放逐了的尸体：同一个实体又活了就马上解除
    banished: Vec<usize>,
    /// 吞掉的（英雄 id，宿主收了放逐没有）：一局的汇总
    pub eaten: Vec<(String, bool)>,
}

/// 场上的英雄实体：英雄列表里的和每个玩家现在的英雄（死了还没复活的尸体在哪边都算上）。
fn bodies(sim: &StableSim<'_>) -> Vec<usize> {
    let mut ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
    for i in 0..sim.player_count() {
        if let Some(id) = sim.player_at(i).and_then(|p| p.champion()).map(|e| e.id()) {
            if !ids.contains(&id) {
                ids.push(id);
            }
        }
    }
    ids
}

impl Shark {
    pub fn tick(&mut self, sim: &mut StableSim<'_>, screen: bool) {
        let tick = sim.tick();
        for id in bodies(sim) {
            if self.seen.contains(&id) {
                continue;
            }
            // the living cost one call a tick; a body is looked at once, the tick it is first seen dead (the bite's mark
            // goes on before its damage, so a body the shark killed carries it then)
            let Some(e) = sim.get_entity(id) else { continue };
            if e.is_alive() {
                continue;
            }
            self.seen.push(id);
            let marked = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).any(|b| b.name() == EAT);
            if e.name().is_some_and(|n| swallows(&n, false, marked)) {
                self.due.push((id, tick + GULP_AFTER));
            }
        }
        let now: Vec<usize> = self.due.iter().filter(|d| d.1 <= tick).map(|d| d.0).collect();
        self.due.retain(|d| d.1 > tick);
        for body in now {
            let Some(e) = sim.get_entity(body) else { continue };
            let (team, pos, name) = (e.team(), e.pos(), e.name().unwrap_or_default());
            let fizz = bodies(sim)
                .into_iter()
                .find(|&c| sim.get_entity(c).is_some_and(|f| f.team() != team && f.name().as_deref() == Some(FIZZ)));
            let ok = sim.entity_banish(fizz.unwrap_or(body), body, GULP_T, if fizz.is_some() { GULP } else { "" }, "");
            if ok {
                self.banished.push(body);
            }
            self.eaten.push((name.clone(), ok));
            say(screen, if ok { "eaten" } else { "eaten refused" },
                format!("{} EATEN {name}#{body} by Fizz's shark at ({}, {}): body banished {GULP_T} ticks{}", head(sim),
                        pos.0, pos.1, if ok { "" } else { " - REFUSED by the host" }));
        }
        // never leave a living champion banished
        for id in std::mem::take(&mut self.banished) {
            match sim.get_entity(id).map(|e| e.is_alive()) {
                Some(true) => {
                    sim.entity_clear_cc(id);
                    say(screen, "eaten back", format!("{} EATEN #{id} lives again: banish cleared", head(sim)));
                }
                Some(false) => self.banished.push(id),
                None => {}
            }
        }
        // the respawned champion is a new entity: forget bodies that are gone
        self.seen.retain(|&id| sim.get_entity(id).is_some_and(|e| !e.is_alive()) || self.due.iter().any(|d| d.0 == id));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sunglasses_wearers() {
        for c in ["league_vayne", "league_locke", "league_heimerdinger", "league_ziggs", "league_twitch", "league_leesin"] {
            assert!(wears_sunglasses(c), "{c}");
        }
        for c in ["league_ezreal", "league_tristana", "league_teemo", "league_aurora", "league_leona", "league_corki"] {
            assert!(!wears_sunglasses(c), "{c}");
        }
    }

    #[test]
    fn one_shade_per_sunlight() {
        assert_eq!(shades_step(0, 0), (false, 0, false));
        assert_eq!(shades_step(1, 0), (false, 1, false), "a new Sunlight: one shade");
        assert_eq!(shades_step(1, 1), (false, 0, true), "kept on while it lasts");
        assert_eq!(shades_step(2, 1), (true, 2, false), "a second hit: two");
        assert_eq!(shades_step(1, 2), (true, 1, false), "one ran out");
        assert_eq!(shades_step(0, 2), (true, 0, false), "all gone");
        let b = shade_buff();
        assert_eq!((b.name(), b.damaged_reduce, b.duration_tick), (SHADES, 1, SHADES_T));
        // Sunlight 10 + shades -1, added before they multiply: 9% more per instance
        assert_eq!(100 + 10 - b.damaged_reduce, 109);
    }

    #[test]
    fn the_shark_swallows_small_yordles_only() {
        assert!(swallows("league_lulu", false, true));
        assert!(swallows("league_annie", false, true));
        assert!(!swallows("league_teemo", false, true), "too heavy");
        assert!(!swallows("league_heimerdinger", false, true), "head too big");
        assert!(!swallows("league_lulu", true, true), "alive");
        assert!(!swallows("league_lulu", false, false), "not the shark's");
        assert!(!swallows("league_garen", false, true));
        assert!(!swallows("league_amumu", false, true));
        assert!(GULP.len() <= BUFF_NAME_CAP && EAT.len() <= BUFF_NAME_CAP);
    }
}
