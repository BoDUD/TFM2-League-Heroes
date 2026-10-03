//! 走一遍真实的导出入口：宿主建图时调地图自定义钩子（给一张 30×30 墙格子），
//! 再在模拟里调 E 的探针，检查日志里画出了地图、探针找到了钩点。只验证 mod 这边的接线。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Doc(HashMap<&'static str, String>);

unsafe extern "C" fn doc_get(
    s: *const c_void,
    path: *const u8,
    len: usize,
    buf: *mut u8,
    cap: usize,
    out_len: *mut usize,
) -> bool {
    let doc = &*(s as *const Doc);
    let path = std::str::from_utf8(std::slice::from_raw_parts(path, len)).unwrap();
    let Some(v) = doc.0.get(path) else { return false };
    *out_len = v.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(v.as_ptr(), buf, v.len().min(cap));
    }
    true
}

struct Unit {
    x: u64,
    y: u64,
    team: usize,
    champion: bool,
}
struct World {
    units: Vec<Unit>,
}
unsafe fn w<'a>(s: *const c_void) -> &'a World {
    &*(s as *const World)
}
unsafe fn unit<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a Unit> {
    w(s).units.get(h.id()?)
}
unsafe extern "C" fn tick(_: *const c_void) -> usize {
    1234
}
unsafe extern "C" fn origin(_: *const c_void, out: *mut SimOriginV1) -> bool {
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 7, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    unit(s, h).is_some()
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(u) = unit(s, h) else { return false };
    *x = u.x;
    *y = u.y;
    true
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    unit(s, h).map_or(0, |u| u.team)
}
unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
    unit(s, h).is_some_and(|u| u.champion)
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    unit(s, h).is_some()
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

#[test]
fn map_dump_and_probe_reach_the_log() {
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_camille_wall::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();

        // 建图：第 10 列整列是墙（cells[y][x]），其余空地。
        let rows: Vec<String> = (0..30)
            .map(|_| format!("[{}]", (0..30).map(|c| if c == 10 { "1" } else { "0" }).collect::<Vec<_>>().join(",")))
            .collect();
        let mut doc = Doc(HashMap::from([
            ("walls", format!("[{}]", rows.join(","))),
            ("nexus_pos", "[[60000,900000],[900000,60000]]".to_string()),
        ]));
        let mut doc_vt: JsonDocVtableV1 = zeroed();
        doc_vt.size = size_of::<JsonDocVtableV1>();
        doc_vt.get_json = Some(doc_get);
        let mut doc_ctx = JsonDocCtxV1 { size: size_of::<JsonDocCtxV1>(), vtable: &doc_vt, state: &mut doc as *mut Doc as *mut c_void };
        let mc = ex.map_customizer;
        ((*mc.vtable).customize.unwrap())(mc.userdata, GameModeKindV1::Moba.code(), &mut doc_ctx);

        // 卡密尔 #0 站在第 8 列中间（x = 8.5 格），墙在 x = 10 格处，敌方英雄 #1 就在墙那边不远。
        let mut world = World {
            units: vec![
                Unit { x: 272_000, y: 480_000, team: 0, champion: true },
                Unit { x: 300_000, y: 500_000, team: 1, champion: true },
                Unit { x: 250_000, y: 480_000, team: 0, champion: false },
            ],
        };
        let mut vt: SimVtableV1 = zeroed();
        vt.size = size_of::<SimVtableV1>();
        vt.tick = Some(tick);
        vt.sim_origin = Some(origin);
        vt.entity_count = Some(count);
        vt.entity_at = Some(at);
        vt.entity_is_valid = Some(valid);
        vt.entity_pos = Some(pos);
        vt.entity_team = Some(team);
        vt.entity_is_champion = Some(champion);
        vt.entity_is_alive = Some(alive);
        let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: &mut world as *mut World as *mut c_void };

        let effects = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let names: Vec<&str> = effects.iter().map(|e| e.name.as_str()).collect();
        assert_eq!(names, ["league_camille_wall:probe_engage", "league_camille_wall:probe_escape"]);
        let engage = effects[0].effect;
        ((*engage.vtable).apply.unwrap())(engage.userdata, &mut ctx, 0, 0, &InputTargetV1::target(2));

        let log = std::fs::read_to_string("league_camille_wall.log").expect("log written");
        let _ = std::fs::remove_file("league_camille_wall.log");
        assert!(log.contains("== map mode=Moba =="), "{log}");
        assert!(log.contains("walls: 30 rows x 30 cols, 30 wall cells"), "{log}");
        assert!(log.contains("00 ..........#..................."), "{log}");
        assert!(log.contains("nexus_pos = [[60000,900000],[900000,60000]]"), "{log}");
        let probe = log.lines().find(|l| l.contains("probe=engage")).expect("probe line");
        assert!(probe.starts_with("[view m=7 s=0] t=1234 probe=engage camille#0 pos=(272000,480000) cell=(8,15) hold=#2 d=22000"), "{probe}");
        // 读法 A（cells[y][x]）：墙在东边 48000 处，英雄都不在墙里，钩点离敌人在 E2 距离内。
        let a = probe.split(" | A[y][x]: ").nth(1).unwrap().split(" | B[x][y]: ").next().unwrap();
        assert!(a.starts_with("champs_in_wall=0/2"), "{a}");
        assert!(a.contains("nearest=47000"), "{a}");
        assert!(!a.contains("engage=none"), "{a}");
    }
}
