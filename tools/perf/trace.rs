// Event trace of a simulated 5v5 match on the classic mod SDK's game_core: do two kits play the same game?
//
//   trace.exe <seconds> <seed> <10 champions: blue top jg mid bot sup, red top jg mid bot sup>
//
// A champion is a .data_champion path or base:<id>. Build it like the balance simulator (sim3.rs) with the SDK's
// build.sh and run it from the folder that holds sim/assets/. Every tick runs with the view's events (a match on
// screen). One line per tick that has events:
//   T <tick> <n events> <hash of the events in order> <hash of the events sorted>
// then the end-of-game statistics like sim3 / tick.exe. Compare the sorted hash of two runs on the same seed
// (tools/perf/same_games.py): the order of a few events (a kill's gold, read from a set) changes between runs of the
// same game. The two fields the engine prints from hash sets (a kill's assisters, the statistics' per-type maps) are
// sorted before hashing.
//
//   TRACE_DUMP=<from>-<to>      every event of those ticks ("E <tick> <event>"), to see where two games part
//   TRACE_HIDE=<prefix>,...     hidden caster flags (no view_buffs entry, no stats) left out of EntityInfo's buff
//                               lists, and an EntityInfo that then equals the unit's last one dropped: for two kits
//                               that name or time their flags differently but play the same
extern crate bincode;
extern crate bumpalo;
extern crate engine_core;
extern crate game_core;
extern crate rand;
extern crate serde_json;

use game_core::*;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::Arc;

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

/// HashMap fields print in a random order (PlayerStatistics' exp_by_type_line_phase): sort the entries of every
/// `: {..}` map that holds no nested braces.
fn canon(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut rest = s;
    while let Some(k) = rest.find(": {") {
        out.push_str(&rest[..k + 2]);
        let after = &rest[k + 3..];
        match after.find('}') {
            Some(len) if !after[..len].contains('{') => {
                let mut parts: Vec<&str> = after[..len].split(", ").collect();
                parts.sort();
                out.push('{');
                out.push_str(&parts.join(", "));
                out.push('}');
                rest = &after[len + 1..];
            }
            _ => {
                out.push('{');
                rest = after;
            }
        }
    }
    out.push_str(rest);
    // a kill's assisters come from a set too
    if let Some(k) = out.find("assist: [") {
        if let Some(len) = out[k + 9..].find(']') {
            let mut parts: Vec<String> = out[k + 9..k + 9 + len].split(", ").map(|x| x.to_string()).collect();
            parts.sort();
            out = format!("{}{}{}", &out[..k + 9], parts.join(", "), &out[k + 9 + len..]);
        }
    }
    out
}

/// TRACE_HIDE=<prefix>,<prefix>: hidden caster flags (no view_buffs entry, no stats) dropped from EntityInfo's buff
/// lists, so two kits that name or time their flags differently compare equal when nothing else differs.
fn hide_buffs(s: &str, hide: &[String]) -> String {
    let k = match s.find("buffs: [") { Some(k) => k + 8, None => return s.to_string() };
    let len = match s[k..].find(']') { Some(l) => l, None => return s.to_string() };
    let kept: Vec<&str> = s[k..k + len].split(", ").filter(|b| {
        let name = b.trim_matches('"');
        !b.is_empty() && !hide.iter().any(|p| name.starts_with(p.as_str()))
    }).collect();
    format!("{}{}{}", &s[..k], kept.join(", "), &s[k + len..])
}

fn h(s: &str) -> u64 {
    let mut x = DefaultHasher::new();
    s.hash(&mut x);
    x.finish()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let secs: usize = args[1].parse().unwrap();
    let seed: u64 = args[2].parse().unwrap();
    let dump: Option<(usize, usize)> = std::env::var("TRACE_DUMP").ok().map(|v| {
        let mut it = v.split('-');
        (it.next().unwrap().parse().unwrap(), it.next().unwrap().parse().unwrap())
    });
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
    let mut stats: Vec<String> = vec![String::new(); 10];
    let mut total = 0usize;
    let mut out = String::new();
    let hide: Vec<String> = std::env::var("TRACE_HIDE").map(|v| v.split(',').map(|x| x.to_string()).collect())
        .unwrap_or_default();
    let mut last_info: std::collections::HashMap<String, String> = std::collections::HashMap::new();
    for t in 0..(60 * secs) {
        bump.reset();
        let frame = match runner.run_tick(&mut bump, true) { Some(f) => f, None => break };
        if frame.events.is_empty() {
            continue;
        }
        let mut lines: Vec<String> = Vec::with_capacity(frame.events.len());
        for e in frame.events.iter() {
            let mut s = canon(&format!("{:?}", e));
            if !hide.is_empty() && s.contains("ty: EntityInfo(") {
                s = hide_buffs(&s, &hide);
                let id = field(&s, "id: ").unwrap_or("").to_string();
                if last_info.get(&id) == Some(&s) {
                    continue;
                }
                last_info.insert(id, s.clone());
            }
            if s.starts_with("PlayerStatistics") {
                let team: usize = field(&s, "team: ").unwrap().parse().unwrap();
                let pos = field(&s, "position: ").unwrap();
                let k = team * 5 + ["Top", "Jungle", "Mid", "Bottom", "Support"].iter().position(|p| *p == pos).unwrap();
                stats[k] = s.clone();
            }
            lines.push(s);
        }
        total += lines.len();
        let ordered = h(&lines.join("\n"));
        if let Some((a, b)) = dump {
            if t >= a && t <= b {
                for s in &lines {
                    out.push_str(&format!("E {} {}\n", t, s));
                }
            }
        }
        lines.sort();
        let sorted = h(&lines.join("\n"));
        out.push_str(&format!("T {} {} {:016x} {:016x}\n", t, lines.len(), ordered, sorted));
    }
    print!("{}", out);
    println!("events {}", total);
    for (k, s) in stats.iter().enumerate() {
        let pick = |f: &str| s.split(&format!(" {}: ", f)).nth(1).map(|x| x.split(',').next().unwrap().to_string()).unwrap_or_default();
        println!("P{} {:14} lvl {} cs {} jungle {} deal {} tank {} heal {} self_heal {} K/D/A {}/{}/{}", k, champs[k],
                 pick("level"), pick("cs"), pick("cs_jungle"), pick("deal"), pick("tank"), pick("heal"), pick("self_heal"),
                 pick("kill"), pick("death"), pick("assist"));
    }
}
