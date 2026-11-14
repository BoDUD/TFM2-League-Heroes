//! 回音击按已损失的生命加伤（0.1.17）：走真实的导出入口，在一个最小的假世界里调用副本里的三个原生效果
//! （`league_leesin_hop:q2` / `q2_qrq` / `q2_rqq`），看补的物理伤害是不是「主包那一下 × 目标已损失生命的比例」，满血、
//! 防御塔、死人不补。假世界只是我们对宿主的猜想，用来检查自己这一边的逻辑。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    hp: usize,
    max: usize,
    attack: usize,
    tower: bool,
    alive: bool,
}

#[derive(Default)]
struct World {
    units: Vec<Unit>,
    /// (attacker, target, amount, damage type code, attack type code)
    damage: Vec<(usize, usize, usize, u32, u32)>,
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
    w(s).units.get_mut(h.id()?)
}
unsafe extern "C" fn tick(_: *const c_void) -> usize {
    100
}
unsafe extern "C" fn origin(_: *const c_void, out: *mut SimOriginV1) -> bool {
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 5, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.tower)
}
unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| !e.tower)
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, e.max);
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    *out = StatV1 { attack: e.attack, ..Default::default() };
    true
}
unsafe extern "C" fn typed(s: *mut c_void, attacker: usize, target: usize, amount: usize, kind: u32, at: u32) -> bool {
    w(s).damage.push((attacker, target, amount, kind, at));
    true
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_tower = Some(tower);
    vt.entity_is_champion = Some(champion);
    vt.entity_hp = Some(hp);
    vt.entity_stat = Some(stat);
    vt.deal_damage_typed = Some(typed);
    vt
}

unsafe fn call(world: &mut World, fx: &HashMap<String, &NativeEffectRegV1>, name: &str, caster: usize, input: InputTargetV1) {
    let vt = vtable();
    let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
    let e = fx[name].effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &input);
}

#[test]
fn every_resonating_strike_adds_its_hit_times_the_missing_health() {
    let log = std::env::temp_dir().join("league_leesin_hop_q2_test.log");
    std::env::set_var("LEAGUE_LEESIN_HOP_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_leesin_hop::tfm2_mod_entry_stable(&host);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: HashMap<String, &NativeEffectRegV1> = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        let lee = Unit { hp: 900, max: 1000, attack: 200, tower: false, alive: true };
        let foe = |hp: usize| Unit { hp, max: 2000, attack: 0, tower: false, alive: true };
        for (site, dmg, ratio) in league_leesin_hop::Q2_SITES {
            let name = format!("league_leesin_hop:{site}");
            assert!(fx.contains_key(&name), "{name} is not registered");
            // a quarter of his health left: +75% of the strike, physical, a skill's
            let mut world = World { units: vec![lee.clone(), foe(500)], ..Default::default() };
            call(&mut world, &fx, &name, 0, InputTargetV1::target(1));
            let strike = dmg + 200 * ratio / 100;
            assert_eq!(world.damage, [(0, 1, strike * 1500 / 2000, DamageTypeV1::Ad.code(), AttackTypeV1::Skill.code())], "{site}");
            // full health, a tower, a dead one, a position instead of a unit: nothing
            for (unit, input) in [(foe(2000), InputTargetV1::target(1)),
                                  (Unit { tower: true, ..foe(500) }, InputTargetV1::target(1)),
                                  (Unit { alive: false, ..foe(500) }, InputTargetV1::target(1)),
                                  (foe(500), InputTargetV1::pos(10, 10))] {
                let mut world = World { units: vec![lee.clone(), unit], ..Default::default() };
                call(&mut world, &fx, &name, 0, input);
                assert!(world.damage.is_empty(), "{site}: {:?}", world.damage);
            }
        }
        let text = std::fs::read_to_string(&log).unwrap_or_default();
        assert!(text.contains(" Q2 q2 #") && text.contains("-> +"), "no Q2 line in the log:\n{text}");
    }
}
