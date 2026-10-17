// CPU cost of a simulated 5v5 match, tick by tick, on the classic mod SDK's game_core (docs/perf.md).
//
//   tick.exe <seconds> <seed> <10 champions: blue top jg mid bot sup, red top jg mid bot sup>
//
// A champion is a .data_champion path or base:<id>. Build it like the balance simulator (sim3.rs) with the
// SDK's build.sh, and run it from the folder that holds sim/assets/ (gs_moba.json, map_setting.bin, ...).
// The first output line gives ticks, events and the CPU cycles this thread spent per tick (mean, p50, p99,
// max), counted with QueryThreadCycleTime, so other programs running at the same time hardly move it.
//
// Environment:
//   TICK_MODE=view    run_tick builds the view's events every tick: a match on screen (default)
//   TICK_MODE=plain   no events: a match simulated in the background
//   TICK_MODE=sparse  events every 60th tick only: the same match as view, about twice as fast, with stats
//   TICK_STATS=1      end-of-game statistics per player (compare two kits on the same seeds)
//   TICK_PROJ=1       every league projectile that lived 600+ ticks (name, caster, lifetime)
extern crate bincode;
extern crate bumpalo;
extern crate engine_core;
extern crate game_core;
extern crate rand;
extern crate serde_json;

use game_core::*;
use std::collections::BTreeMap;
use std::sync::Arc;

#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentThread() -> isize;
    fn QueryThreadCycleTime(h: isize, cycles: *mut u64) -> i32;
}

fn cycles() -> u64 {
    let mut c = 0u64;
    unsafe { QueryThreadCycleTime(GetCurrentThread(), &mut c) };
    c
}

fn load_champ(path: &str) -> (String, Arc<dyn ChampionInfo>) {
    let raw = std::fs::read_to_string(path).unwrap();
    let data: DataChampionInfo = serde_json::from_str(raw.trim_start_matches('\u{feff}')).unwrap();
    let entry = ModChampionEntry::from_data_champion_info(&data, None);
    (data.id.clone(), Arc::new(entry))
}

fn athlete() -> AthleteStat {
    let mut st = AthleteStat::default();
    for v in [&mut st.aggressive, &mut st.bottom, &mut st.concentration, &mut st.control_speed, &mut st.ego,
              &mut st.judgement, &mut st.jungle, &mut st.last_hit, &mut st.mental, &mut st.mid, &mut st.order,
              &mut st.positioning, &mut st.roaming, &mut st.skill_avoid, &mut st.skill_hit, &mut st.support, &mut st.top] {
        *v = 50;
    }
    st
}

fn field<'a>(s: &'a str, key: &str) -> Option<&'a str> {
    s.split(key).nth(1).map(|x| x.split(|c| c == ',' || c == ' ' || c == '}').next().unwrap_or(""))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let secs: usize = args[1].parse().unwrap();
    let seed: u64 = args[2].parse().unwrap();
    let mode = std::env::var("TICK_MODE").unwrap_or_else(|_| "view".to_string());
    let want_stats = std::env::var("TICK_STATS").is_ok();
    let want_proj = std::env::var("TICK_PROJ").is_ok();
    let gs: GameSetting = serde_json::from_str(&std::fs::read_to_string("sim/assets/gs_moba.json").unwrap()).unwrap();
    let ms: MapSetting = bincode::deserialize(&std::fs::read("sim/assets/map_setting.bin").unwrap()).unwrap();
    let mw: MacroWeights = serde_json::from_str(&std::fs::read_to_string("sim/assets/macro_weights.json").unwrap()).unwrap();
    let is: ItemSetting = serde_json::from_str(&std::fs::read_to_string("sim/assets/item_setting.json").unwrap()).unwrap();
    let cs: Arc<ChampionInfoSheet> = Arc::new(serde_json::from_str(&std::fs::read_to_string("sim/assets/champion_info.json").unwrap()).unwrap());
    let mut runner = GameRunner::new(seed, false, Arc::new(gs), Arc::new(ms), Arc::new(is), cs.clone());
    runner.set_macro_weights(Arc::new(mw));
    let positions = [Position::Top, Position::Jungle, Position::Mid, Position::Bottom, Position::Support];
    let mut champs = vec![];
    for k in 0..10 {
        let (id, info) = match args[3 + k].strip_prefix("base:") {
            Some(b) => (b.to_string(), cs.get_champion_info(b).expect("base champion")),
            None => load_champ(&args[3 + k]),
        };
        let p = GamePlayer::new(k, &format!("P{}", k), k / 5, positions[k % 5], athlete(), &id, info, vec![]);
        runner.add_player(p);
        champs.push(id);
    }
    let mut bump = bumpalo::Bump::new();
    let mut per_tick: Vec<u64> = Vec::with_capacity(60 * secs);
    let mut stats: Vec<String> = vec![String::new(); 10];
    let mut proj: BTreeMap<u64, (String, String, usize, usize)> = BTreeMap::new(); // id -> name, caster, first, last
    let mut n_events = 0usize;
    let mut ended = None;
    for t in 0..(60 * secs) {
        bump.reset();
        let view = match mode.as_str() { "plain" => false, "sparse" => t % 60 == 0, _ => true };
        let c0 = cycles();
        let frame = runner.run_tick(&mut bump, view);
        per_tick.push(cycles() - c0);
        let frame = match frame { Some(f) => f, None => { ended = Some(t); break; } };
        n_events += frame.events.len();
        if want_stats || want_proj {
            for e in frame.events.iter() {
                let s = format!("{:?}", e);
                if want_stats && s.starts_with("PlayerStatistics") {
                    let team: usize = field(&s, "team: ").unwrap().parse().unwrap();
                    let pos = field(&s, "position: ").unwrap();
                    let k = team * 5 + ["Top", "Jungle", "Mid", "Bottom", "Support"].iter().position(|p| *p == pos).unwrap();
                    stats[k] = s;
                } else if want_proj && s.starts_with("ProjectileSpawnData") {
                    let id: u64 = field(&s, "id: ").unwrap().parse().unwrap();
                    let name = s.split("name: \"").nth(1).unwrap_or("").split('"').next().unwrap_or("").to_string();
                    if name.starts_with("league_") {
                        proj.insert(id, (name, field(&s, "caster_id: ").unwrap_or("?").to_string(), t, t));
                    }
                } else if want_proj && s.starts_with("ProjectileMove") {
                    let id: u64 = field(&s, "id: ").unwrap().parse().unwrap();
                    if let Some(p) = proj.get_mut(&id) { p.3 = t; }
                }
            }
        }
    }
    let n = per_tick.len();
    let mut sorted = per_tick.clone();
    sorted.sort();
    let mean = per_tick.iter().sum::<u64>() as f64 / n as f64;
    println!("ticks {} ended {:?} events {} cyc_tick_mean {:.0} p50 {} p99 {} max {}",
             n, ended, n_events, mean, sorted[n / 2], sorted[n * 99 / 100], sorted[n - 1]);
    let minutes: Vec<String> = per_tick.chunks(3600).map(|c| format!("{:.0}", c.iter().sum::<u64>() as f64 / c.len() as f64)).collect();
    println!("per_minute_cyc {}", minutes.join(","));
    if want_stats {
        for (k, s) in stats.iter().enumerate() {
            let pick = |f: &str| s.split(&format!(" {}: ", f)).nth(1).map(|x| x.split(',').next().unwrap().to_string()).unwrap_or_default();
            println!("P{} {:14} lvl {} cs {} jungle {} deal {} tank {} heal {} self_heal {} K/D/A {}/{}/{}", k, champs[k],
                     pick("level"), pick("cs"), pick("cs_jungle"), pick("deal"), pick("tank"), pick("heal"), pick("self_heal"),
                     pick("kill"), pick("death"), pick("assist"));
        }
    }
    if want_proj {
        for (id, (name, caster, first, last)) in &proj {
            if last - first >= 600 {
                println!("long-lived projectile {} {} caster {} ticks {}..{} ({} ticks)", id, name, caster, first, last, last - first);
            }
        }
    }
}
