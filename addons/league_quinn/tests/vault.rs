//! 走真实的导出入口，在假宿主里试旋翔掠杀踢完往后翻（0.7.2，用户 2026-11-21：「我看局内是不会后空翻的」）：
//! - 踢中的那一 tick 本包给她一段强制位移（往冲过来的方向 48000：20 tick x 2400），宿主照着挪，她停在落点，本包一步都不用自己走；
//! - 宿主不执行强制位移（被挡住之类）时本包自己一步步走到落点；
//! - 被踢的单位死了、数据的踢中效果一个都没跑（身上没有踢中的标记、没有 e_flip）也照样翻，e_flip 由本包补上；
//! - 两种情况下逐帧标记 `league_quinn_flip0` … `flip6` 都按后空翻每帧的时间依次挂 36 tick，一次只挂一个。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

#[derive(Default)]
struct World {
    tick: usize,
    x: f64,
    y: f64,
    buffs: Vec<BuffV1>,
    ccs: Vec<CcV1>,
    /// 宿主执不执行强制位移。
    moves: bool,
    /// 本包直接改坐标的次数。
    placed: usize,
    /// 别的单位：敌方小兵（被踢的）。
    foe: (f64, f64),
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe extern "C" fn tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn origin(_: *const c_void, out: *mut SimOriginV1) -> bool {
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 7, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn count(_: *const c_void) -> usize {
    2
}
unsafe extern "C" fn at(_: *const c_void, i: usize) -> EntityHandleV1 {
    EntityHandleV1::from_id(i)
}
unsafe extern "C" fn valid(_: *const c_void, h: EntityHandleV1) -> bool {
    h.id().is_some_and(|i| i < 2)
}
unsafe extern "C" fn yes(_: *const c_void, _: EntityHandleV1) -> bool {
    true
}
unsafe extern "C" fn is_champion(_: *const c_void, h: EntityHandleV1) -> bool {
    h.id() == Some(0)
}
unsafe extern "C" fn no(_: *const c_void, _: EntityHandleV1) -> bool {
    false
}
unsafe extern "C" fn is_minion(_: *const c_void, h: EntityHandleV1) -> bool {
    h.id() == Some(1)
}
unsafe extern "C" fn kind(_: *const c_void, h: EntityHandleV1) -> u32 {
    if h.id() == Some(0) { EntityKindV1::Champion.code() } else { EntityKindV1::Minion.code() }
}
unsafe extern "C" fn team(_: *const c_void, h: EntityHandleV1) -> usize {
    h.id().unwrap_or(0)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let world = w(s);
    let p = if h.id() == Some(0) { (world.x, world.y) } else { world.foe };
    (*x, *y) = (p.0.round() as u64, p.1.round() as u64);
    true
}
unsafe extern "C" fn hp(_: *const c_void, _: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    (*now, *max) = (1000, 1000);
    true
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    if h.id() == Some(0) { w(s).buffs.len() } else { 0 }
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    if h.id() != Some(0) {
        return false;
    }
    let Some(b) = w(s).buffs.get(i) else { return false };
    *out = *b;
    true
}
unsafe extern "C" fn cc_count(s: *const c_void, h: EntityHandleV1) -> usize {
    if h.id() == Some(0) { w(s).ccs.len() } else { 0 }
}
unsafe extern "C" fn cc_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut CcV1) -> bool {
    if h.id() != Some(0) {
        return false;
    }
    let Some(c) = w(s).ccs.get(i) else { return false };
    *out = *c;
    true
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if id == 0 {
        w(s).buffs.push(*b);
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    if h.id() != Some(0) {
        return 0;
    }
    let name = std::str::from_utf8(std::slice::from_raw_parts(n, len)).unwrap();
    let world = w(s);
    let before = world.buffs.len();
    world.buffs.retain(|b| b.name() != name);
    before - world.buffs.len()
}
unsafe extern "C" fn apply_cc(s: *mut c_void, id: usize, cc: *const CcV1) {
    let world = w(s);
    if id == 0 && ((*cc).kind != CcKindV1::ForceMove.code() || world.moves) {
        world.ccs.push(*cc);
    }
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    if h.id() != Some(0) {
        return false;
    }
    let world = w(s);
    (world.x, world.y) = (x as f64, y as f64);
    world.placed += 1;
    true
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(yes);
    vt.entity_is_targetable = Some(yes);
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_tower = Some(no);
    vt.entity_is_minion = Some(is_minion);
    vt.entity_kind = Some(kind);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.apply_cc = Some(apply_cc);
    vt.entity_set_pos = Some(set_pos);
    vt
}

/// 宿主的一 tick：强制位移挪她（每 tick `speed`，朝 (dx, dy)），控制和 buff 各少一 tick、到 0 就没了。
fn host_tick(world: &mut World) {
    for c in world.ccs.iter() {
        if c.kind == CcKindV1::ForceMove.code() {
            let len = ((c.dx as f64).powi(2) + (c.dy as f64).powi(2)).sqrt();
            if len > 0.0 {
                world.x += c.dx as f64 / len * c.speed as f64;
                world.y += c.dy as f64 / len * c.speed as f64;
            }
        }
    }
    for c in world.ccs.iter_mut() {
        c.tick = c.tick.saturating_sub(1);
    }
    world.ccs.retain(|c| c.tick > 0);
    for b in world.buffs.iter_mut() {
        b.duration_tick = b.duration_tick.saturating_sub(1);
    }
    world.buffs.retain(|b| b.duration_tick > 0);
    world.tick += 1;
}

fn flag_on(world: &World) -> Vec<usize> {
    (0..league_quinn::FLIP_MS.len()).filter(|&k| world.buffs.iter().any(|b| b.name() == league_quinn::flip_buff(k))).collect()
}

fn anim(name: &str, ticks: u64) -> CcV1 {
    let mut a = CcV1::of_kind(CcKindV1::Animation, ticks);
    a.set_name(name);
    a
}

#[test]
fn the_vault_is_a_forced_move_and_the_flip_goes_frame_by_frame() {
    let log = std::env::temp_dir().join(format!("league_quinn_vault_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_QUINN_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_quinn::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_quinn:ride"]);
        let proto = &passives[0].passive;
        let fresh = || PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let update = |p: &PassiveRegV1, world: &mut World| {
            let vt = vtable();
            let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
            ((*p.vtable).on_update.unwrap())(p.userdata, &mut ctx, 0, 0, 0);
        };
        // 她从左边冲过来：出 E 的标记在身上，每 tick 往右 4000，10 tick 后到被踢的小兵身上（540000, 500000）
        let dash_in = |p: &PassiveRegV1, world: &mut World| {
            world.buffs.push(BuffV1::timed(league_quinn::DASH, league_quinn::DASH_T));
            for _ in 0..10 {
                update(p, world);
                world.x += 4000.0;
                host_tick(world);
            }
            assert_eq!((world.x, world.y), (540_000.0, 500_000.0));
        };
        let frames_by_tick: Vec<usize> = (0..36).map(|t| league_quinn::flip_frame(t).unwrap()).collect();

        // 1. 宿主执行强制位移：踢中的那一 tick 给了一段 20 tick x 2400 的位移，她停在落点，本包一步没自己走
        let p = fresh();
        let mut world = World { tick: 1000, x: 500_000.0, y: 500_000.0, moves: true, foe: (540_000.0, 500_000.0), ..Default::default() };
        dash_in(&p, &mut world);
        world.buffs.push(BuffV1::timed(league_quinn::VAULT, 4)); // 数据的踢中效果：标记、后空翻动作
        world.ccs.push(anim("e_flip", 36));
        let mut seen = vec![];
        for t in 0..44 {
            update(&p, &mut world);
            if t == 0 {
                let mv: Vec<&CcV1> = world.ccs.iter().filter(|c| c.kind == CcKindV1::ForceMove.code()).collect();
                assert_eq!(mv.len(), 1, "no forced move at the kick");
                assert_eq!((mv[0].dx, mv[0].dy, mv[0].speed, mv[0].tick), (-48_000, 0, 2400, 20));
                assert_eq!(world.ccs.iter().filter(|c| c.kind == CcKindV1::Animation.code()).count(), 1, "a second e_flip");
            }
            seen.push(flag_on(&world));
            host_tick(&mut world);
        }
        assert_eq!((world.x, world.y), (492_000.0, 500_000.0), "she did not land 48000 back");
        assert_eq!(world.placed, 0, "the add-on stepped her though the host moved her");
        for (t, f) in seen.iter().enumerate() {
            let want: Vec<usize> = frames_by_tick.get(t).map(|k| vec![*k]).unwrap_or_default();
            assert_eq!(*f, want, "flip flags at tick {t}");
        }

        // 2. 宿主不执行强制位移：本包自己一步步走到落点（晚一 tick 起步），标记照样一帧一帧挂
        let p = fresh();
        let mut world = World { tick: 2000, x: 500_000.0, y: 500_000.0, moves: false, foe: (540_000.0, 500_000.0), ..Default::default() };
        dash_in(&p, &mut world);
        world.buffs.push(BuffV1::timed(league_quinn::VAULT, 4));
        world.ccs.push(anim("e_flip", 36));
        let mut seen = vec![];
        for _ in 0..44 {
            update(&p, &mut world);
            seen.push(flag_on(&world));
            host_tick(&mut world);
        }
        assert_eq!((world.x, world.y), (492_000.0, 500_000.0), "she did not get there on her own steps");
        assert_eq!(world.placed, 20);
        assert_eq!(seen[..36].iter().map(|f| f[0]).collect::<Vec<_>>(), frames_by_tick);
        assert!(seen[36..].iter().all(|f| f.is_empty()));

        // 3. 被踢的小兵死了，数据的踢中效果一个都没跑（没有标记、没有 e_flip）：冲刺停下的那一 tick（她不再往前挪的第一 tick，
        //    比踢中的标记晚一 tick）本包照样翻，e_flip 自己补
        let p = fresh();
        let mut world = World { tick: 3000, x: 500_000.0, y: 500_000.0, moves: true, foe: (540_000.0, 500_000.0), ..Default::default() };
        dash_in(&p, &mut world);
        let mut seen = vec![];
        for t in 0..44 {
            update(&p, &mut world);
            if t == 0 {
                assert!(world.ccs.is_empty() && flag_on(&world).is_empty(), "she flipped before her dash stopped");
            }
            if t == 1 {
                assert!(world.ccs.iter().any(|c| c.kind == CcKindV1::Animation.code() && c.name() == "e_flip" && c.tick == 36),
                        "the add-on did not play e_flip itself");
                assert!(world.ccs.iter().any(|c| c.kind == CcKindV1::ForceMove.code()));
            }
            seen.push(flag_on(&world));
            host_tick(&mut world);
        }
        assert_eq!((world.x, world.y), (492_000.0, 500_000.0));
        assert_eq!(seen[1..37].iter().map(|f| f[0]).collect::<Vec<_>>(), frames_by_tick);
        assert!(seen[37..].iter().all(|f| f.is_empty()));
    }
    let text = std::fs::read_to_string(&log).unwrap();
    for want in [
        "VAULT (the kick's flag) flip back (-1.00, 0.00), the way she dashed in: forced move 20 ticks x 2400 over 48000",
        "VAULT DONE moved 48000 of 48000 in 20 ticks (0 steps of her own)",
        "VAULT DONE moved 48000 of 48000 in 21 ticks (20 steps of her own)",
        "VAULT (the dash stopped) flip back (-1.00, 0.00), the way she dashed in",
        "FLIP over after 36 ticks",
    ] {
        assert!(text.contains(want), "no line `{want}` in\n{text}");
    }
}
