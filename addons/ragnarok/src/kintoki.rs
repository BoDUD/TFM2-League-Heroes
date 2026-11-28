//! 坂田金时（`ragnarok_kintoki`）数据做不到的部分。数据（tools/kit/build_kintoki.py）的 `passive` 是这里的
//! `ragnarok_kintoki:oni`，参数从数据的 `passive.params` 来（build_kintoki.py 的参数表 P，`NATIVE_KEYS`）。
//!
//! - 鬼之血（「我身上流着老妈的鬼之血，还没完呢！」）：每拍按损失的生命改攻击力：buff `ragnarok_kintoki_p_oni`，
//!   攻击力 +损失的生命% × `p_per` / 10%，最多 `p_max`%。加成变了才换 buff。
//! - 絶技・金光轟雷斧击碎护盾（漫画第 126 话一下击碎奥丁的神环封壁）：大招砸中时目标身上挂着 `ragnarok_kintoki_r_shatter`
//!   （数据在伤害前一刻挂上），这一下打之前把它的护盾清零，奥丁的神环封壁（buff `ragnarok_odin_e_ward`）一起碎掉。
//! - 徒手接住冈格尼尔（第 116 话）：奥丁的冈格尼尔打中他（他身上挂着 `ragnarok_odin_q_mark`、打他的是奥丁）时，这一下只吃
//!   100 - `k_catch`%（挨打前把那一截血补回去，补不满的下一拍补），`K_HOLD` 拍以后把枪掷回奥丁：弹道真的飞回去（画面是奥丁的
//!   冈格尼尔），到了造成冈格尼尔那一下 `k_back`% 的真实伤害；冈格尼尔连奥丁自己的护盾和神环封壁也穿过去。
//! - 倒地：死的时候放 Codex 的倒地声（延迟在 sound_info 里）。没有配音（官方日语的找不到）。
//!
//! 经典 SDK 跑不了这里的代码，平衡模拟用 build_kintoki.py --plain（鬼之血换成平均加成，没有击碎护盾和接枪）。
//! 日志写在本包的 ragnarok.log 里（行首 `kintoki`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::skill_scale::sk;
use mod_api_stable::*;

const ID: &str = "ragnarok_kintoki";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 第十二回合的对手奥丁和他的两个标记
pub const ODIN_ID: &str = "ragnarok_odin";
pub const ODIN_SPEAR_MARK: &str = "ragnarok_odin_q_mark";
pub const ODIN_WARD: &str = "ragnarok_odin_e_ward";
/// 接住以后多久掷回去（拍）：按进地里、借着召回的力道转身掷出
pub const K_HOLD: usize = 20;
/// 掷回去的枪每拍飞多远（冈格尼尔自己是 6000；大地图版两边一起乘 1.3）
pub const K_SPEED: u64 = 6_000;
/// 掷回去的弹道打中时做的事（本包的原生效果）
const SPEAR_BACK: &str = "ragnarok_kintoki:spear_back";

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
        crate::wlog(format!("kintoki [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 每损失 1% 生命加多少攻击力（千分之几）
    pub p_per: usize,
    /// 鬼之血最多加多少攻击力（%）
    pub p_max: usize,
    /// 接住冈格尼尔时少吃多少（%）
    pub k_catch: usize,
    /// 掷回去造成冈格尼尔那一下的多少（%）
    pub k_back: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_per: 4, p_max: 30, k_catch: 50, k_back: 100 }
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
            "p_per" => p.p_per = u.min(100),
            "p_max" => p.p_max = u.min(300),
            "k_catch" => p.k_catch = u.min(100),
            "k_back" => p.k_back = u.min(1000),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 鬼之血：生命 hp / max 时加多少攻击力（%）。
pub fn oni_bonus(hp: usize, max: usize, p: &Params) -> usize {
    if max == 0 {
        return 0;
    }
    let missing = max.saturating_sub(hp) * 100 / max;
    (missing * p.p_per / 10).min(p.p_max)
}

/// 补血：(补完的生命, 补不下的那一截)。
pub fn refund(hp: usize, max: usize, back: usize) -> (usize, usize) {
    let room = max.saturating_sub(hp);
    (hp + back.min(room), back.saturating_sub(room))
}

/// 鬼之血的 buff（永久，加成变了就换一个）。
pub fn oni_buff(bonus: usize) -> BuffV1 {
    let mut b = BuffV1::named(&vo("p_oni"));
    b.attack_mult = bonus as i32;
    b
}

// ===================== 游戏里 =====================

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 等着掷回去的冈格尼尔：哪一拍掷、掷向谁、到了打多少。
#[derive(Clone, Copy, Debug)]
struct Throw {
    at: usize,
    odin: usize,
    damage: usize,
}

/// 飞在路上的冈格尼尔：(金时, 奥丁) -> 到了打多少（打中时原生效果来取）。
static FLYING: LazyLock<Mutex<HashMap<(usize, usize), usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

#[derive(Clone, Default)]
struct KintokiPassive {
    p: Params,
    me: usize,
    was_alive: bool,
    /// 现在挂着的鬼之血加成（%）
    oni: Option<usize>,
    /// 接枪时补不下的血，下一拍补
    owed: usize,
    throws: Vec<Throw>,
}

impl KintokiPassive {
    fn throw_back(&mut self, sim: &mut StableSim<'_>, t: Throw) {
        let me = self.me;
        let Some((my_pos, team)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team())) else {
            return;
        };
        if !sim.get_entity(t.odin).is_some_and(|o| o.is_alive()) {
            log(sim, format!("SPEAR #{me}: Odin #{} is gone, nothing thrown back", t.odin));
            return;
        }
        FLYING.lock().unwrap_or_else(|e| e.into_inner()).insert((me, t.odin), t.damage);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: my_pos.0,
            y: my_pos.1,
            radius: 10_000,
            speed: sk(K_SPEED),
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: t.odin,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyChampion.code(),
        };
        let ok = sim.spawn_projectile(&vo("k_back"), SPEAR_BACK, &spec);
        sim.play_sfx(&vo("k_throw"), me, &InputTargetV1::target(me));
        log(sim, format!("SPEAR #{me}: Gungnir thrown back at Odin #{} for {} true damage{}", t.odin, t.damage,
                         if ok { "" } else { " - spawn_projectile refused" }));
    }
}

impl StablePassive for KintokiPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，身上的 buff 都没了：鬼之血重新挂
        self.was_alive = false;
        self.me = me;
        self.oni = None;
        self.owed = 0;
        self.throws.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Kintoki (player {player}, team {team}), {:?}", self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, me: usize) {
        self.me = me;
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {
            self.oni = None;
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
        let (hp, max) = sim.get_entity(me).map_or((hp, max), |e| e.hp());
        let bonus = oni_bonus(hp, max, &self.p);
        if self.oni != Some(bonus) {
            sim.entity_remove_buff(me, &vo("p_oni"));
            if bonus > 0 {
                sim.add_buff(me, &oni_buff(bonus));
            }
            self.oni = Some(bonus);
        }
        let now = sim.tick();
        let (due, wait): (Vec<Throw>, Vec<Throw>) = self.throws.drain(..).partition(|t| t.at <= now);
        self.throws = wait;
        for t in due {
            self.throw_back(sim, t);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let shatter = vo("r_shatter");
        let Some((marked, shield)) = sim.get_entity(target).map(|t| (has_buff(&t, &shatter), t.shield())) else {
            return;
        };
        if !marked {
            return;
        }
        // 一个目标只碎一次（同一拍别的伤害不再算）
        sim.entity_remove_buff(target, &shatter);
        let layers = sim.entity_clear_shield(target);
        let ward = sim.entity_remove_buff(target, ODIN_WARD);
        if layers > 0 || ward > 0 {
            sim.play_sfx(&vo("r_shatter"), me, &InputTargetV1::target(target));
        }
        log(sim, format!("SHATTER #{me}: #{target} shield {shield} ({layers} layers){}", if ward > 0 {
            ", Odin's Fafnir broken"
        } else {
            ""
        }));
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        self.me = me;
        if damage == 0 {
            return;
        }
        let Some((alive, (hp, max), caught)) =
            sim.get_entity(me).map(|e| (e.is_alive(), e.hp(), has_buff(&e, ODIN_SPEAR_MARK)))
        else {
            return;
        };
        if !alive || !caught {
            return;
        }
        if sim.get_entity(attacker).and_then(|a| a.name()).as_deref() != Some(ODIN_ID) {
            return;
        }
        // 这一下在扣血之前：先把要少吃的那一截补上（补不下的下一拍补）
        sim.entity_remove_buff(me, ODIN_SPEAR_MARK);
        let back = damage * self.p.k_catch / 100;
        let (set, over) = refund(hp, max, back);
        sim.entity_set_hp(me, set);
        self.owed += over;
        let now = sim.tick();
        self.throws.push(Throw { at: now + K_HOLD, odin: attacker, damage: damage * self.p.k_back / 100 });
        sim.play_sfx(&vo("k_catch"), me, &InputTargetV1::target(me));
        log(sim, format!("CATCH #{me}: Gungnir {damage} from Odin #{attacker}, {back} caught; thrown back in {K_HOLD} ticks"));
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        self.oni = None;
        self.owed = 0;
        self.throws.clear();
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

/// 掷回去的冈格尼尔打中奥丁：真实伤害，先穿过他的护盾和神环封壁。
#[derive(Debug)]
struct SpearBack;

impl StableEffectType for SpearBack {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        let odin = input.target_id;
        let damage = FLYING.lock().unwrap_or_else(|e| e.into_inner()).remove(&(caster, odin)).unwrap_or(0);
        if damage == 0 || !sim.get_entity(odin).is_some_and(|o| o.is_alive()) {
            return;
        }
        sim.entity_clear_shield(odin);
        sim.entity_remove_buff(odin, ODIN_WARD);
        sim.deal_damage_typed(caster, odin, damage, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        let on = InputTargetV1::target(odin);
        sim.play_view_effect(&vo("k_back_hit"), caster, &on, 0, 0, 0);
        sim.play_sfx(&vo("k_back_hit"), caster, &on);
        log(sim, format!("SPEAR #{caster}: Gungnir back into Odin #{odin}, {damage} true damage"));
    }
}

// ===================== 注册 =====================

/// 坂田金时的被动和接枪的原生效果，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("kintoki: {ID} v{VERSION} (Kintoki: Oni's Blood, the shattering axe, Gungnir caught and thrown back, the fall) registered"));
    module.add_native_passive(format!("{ID}:oni"), KintokiPassive::default());
    module.add_native_effect(SPEAR_BACK, SpearBack);
    host.log(LogLevel::Info, "ragnarok.dll: Sakata Kintoki (Oni's Blood, Golden Light Roaring Thunder Axe, Gungnir caught).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"k_back":100,"k_catch":50,"p_max":30,"p_per":4}"#;
        assert_eq!(parse_params(json), Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"k_catch":250}"#).k_catch, 100);
    }

    /// 每少 1% 生命 +0.4% 攻击力，最多 +30%（少 75% 生命就满了）。
    #[test]
    fn oni_grows_with_the_wounds() {
        let p = Params::default();
        assert_eq!(oni_bonus(1000, 1000, &p), 0);
        assert_eq!(oni_bonus(900, 1000, &p), 4);
        assert_eq!(oni_bonus(500, 1000, &p), 20);
        assert_eq!(oni_bonus(250, 1000, &p), 30);
        assert_eq!(oni_bonus(1, 1000, &p), 30);
        assert_eq!(oni_bonus(0, 0, &p), 0);
    }

    #[test]
    fn the_oni_buff() {
        let b = oni_buff(12);
        assert_eq!(b.name(), "ragnarok_kintoki_p_oni");
        assert_eq!(b.attack_mult, 12);
        assert_eq!(b.duration_kind, BuffDurationV1::Permanent.code());
    }

    #[test]
    fn a_refund_never_passes_max_health() {
        assert_eq!(refund(500, 1000, 200), (700, 0));
        assert_eq!(refund(900, 1000, 200), (1000, 100));
        assert_eq!(refund(1000, 1000, 50), (1000, 50));
    }
}
