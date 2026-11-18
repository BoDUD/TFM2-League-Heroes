//! 英雄联盟赛事（用户 2026-11-18：「能不能做个赛事mod啊 现在比赛赛事不像英雄联盟 每年也太固定了」；选了「换成英雄联盟的
//! 名字」「每年赛制会变」「赛程日期和赛事每年浮动」，无畏征召用游戏自带的）。
//!
//! 生涯里的赛事是游戏自己的：6 个赛区各一个一级、二级联赛（春季、夏季，季后赛、升降级），4 个国际赛（东 / 西挑战者杯、
//! 大师赛、冠军赛），每年的日程（`YearSchedule`：哪天开招募、开哪个联赛、打第几轮、哪天抽签、哪天打国际赛）和赛制都一样。
//!
//! - **0.0.1**：
//!   - 名字换成英雄联盟的（`text/ui.i18n` 合进游戏的 `asset/base/text/ui`）：LCK / LPL / LEC / LCS / CBLOL / LJL，二级联赛
//!     LCK CL / LDL / ERL / NACL / CBLOL 学院 / LJL 学院，大师赛叫季中冠军赛（MSI），冠军赛叫全球总决赛，东 / 西挑战者杯叫
//!     洲际赛（东部 / 西部）。
//!   - 只读的探测（[`probe`]）：游戏载入生涯后第一次跑经营 tick 时，把全年赛程、联赛 / 杯赛的定义和每一届、几场比赛的
//!     样子、比赛规则设置原样写进 `league_esports_probe.json`，什么都不改。每年变赛制、变赛程要先看清这些记录，下一版再做。
//!   - 日志 `league_esports.log`：载入、探测写了什么、赛季切换（`SeasonRollover`）的内容。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex, PoisonError};

use mod_api_stable::*;

const ID: &str = "league_esports";
const VERSION: &str = env!("CARGO_PKG_VERSION");

// ===================== 日志、文件 =====================

fn data_dir() -> PathBuf {
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir;
        }
    }
    PathBuf::from(".")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(|| match std::env::var_os("LEAGUE_ESPORTS_LOG") {
    Some(p) => PathBuf::from(p),
    None => data_dir().join("league_esports.log"),
});
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn wlog(msg: impl AsRef<str>) {
    let mut file = LOG_FILE.lock().unwrap_or_else(PoisonError::into_inner);
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

// ===================== 读记录 =====================

/// The integers of a JSON fragment, in order (a match list's ids; nested lists come out flat).
pub fn ints(json: &str) -> Vec<usize> {
    let mut out = Vec::new();
    let mut cur: Option<usize> = None;
    for ch in json.chars() {
        match ch.to_digit(10) {
            Some(d) => cur = Some(cur.unwrap_or(0).saturating_mul(10).saturating_add(d as usize)),
            None => out.extend(cur.take()),
        }
    }
    out.extend(cur);
    out
}

/// `"name": value,` for the probe document (value is JSON already).
pub fn field(out: &mut String, name: &str, value: &str) {
    if out.len() > 2 {
        out.push_str(",\n");
    }
    out.push_str(&format!("\"{name}\": {value}"));
}

/// `[a, b, ...]` of JSON values.
pub fn array(items: &[String]) -> String {
    format!("[\n{}\n]", items.join(",\n"))
}

/// Every record of `kind`, whole, as `{"id": n, "record": ...}`.
fn all(ctx: &StableServerCtx<'_>, kind: RecordKindV1) -> Vec<String> {
    ctx.record_ids(kind)
        .into_iter()
        .map(|id| format!("{{\"id\": {id}, \"record\": {}}}", ctx.record_get_json(kind, id, "").unwrap_or_else(|| "null".into())))
        .collect()
}

/// The ids under `path` of a record (a competition's match list).
fn ids_at(ctx: &StableServerCtx<'_>, kind: RecordKindV1, id: usize, path: &str) -> Vec<usize> {
    ctx.record_get_json(kind, id, path).map(|s| ints(&s)).unwrap_or_default()
}

/// A few of a list: the first `n` and the last one.
pub fn sample(list: &[usize], n: usize) -> Vec<usize> {
    let mut out: Vec<usize> = list.iter().copied().take(n).collect();
    if let Some(&last) = list.last() {
        if !out.contains(&last) {
            out.push(last);
        }
    }
    out
}

/// The read-only probe: the year schedules, the leagues and tournaments (definitions and every edition), a few matches
/// of each stage and the game rules, as the game hands them to a mod, into `league_esports_probe.json`.
fn probe(ctx: &StableServerCtx<'_>) -> std::io::Result<(PathBuf, String)> {
    let mut out = String::from("{\n");
    field(&mut out, "probe", &format!("\"{ID} v{VERSION}\""));
    let kinds = [
        ("teams", RecordKindV1::Team),
        ("athletes", RecordKindV1::Athlete),
        ("leagues", RecordKindV1::League),
        ("tournaments", RecordKindV1::Tournament),
        ("league_competitions", RecordKindV1::LeagueCompetition),
        ("tournament_competitions", RecordKindV1::TournamentCompetition),
        ("year_schedules", RecordKindV1::YearSchedule),
        ("matches", RecordKindV1::Match),
    ];
    let counts: Vec<String> = kinds.iter().map(|(n, k)| format!("\"{n}\": {}", ctx.record_ids(*k).len())).collect();
    field(&mut out, "counts", &format!("{{{}}}", counts.join(", ")));
    field(&mut out, "game_setting", &ctx.setting_get_json(SettingTargetV1::GameSetting, "").unwrap_or_else(|| "null".into()));
    for (name, kind) in [
        ("year_schedules", RecordKindV1::YearSchedule),
        ("leagues", RecordKindV1::League),
        ("tournaments", RecordKindV1::Tournament),
        ("tournament_competitions", RecordKindV1::TournamentCompetition),
        ("league_competitions", RecordKindV1::LeagueCompetition),
    ] {
        field(&mut out, name, &array(&all(ctx, kind)));
    }
    // a few matches of every stage: each tournament edition's groups and knockouts, the newest league editions' stages
    let mut picked: Vec<(String, usize)> = Vec::new();
    for id in ctx.record_ids(RecordKindV1::TournamentCompetition) {
        for path in ["group_matches", "tournament_matches"] {
            for m in sample(&ids_at(ctx, RecordKindV1::TournamentCompetition, id, path), 3) {
                picked.push((format!("tournament_competition {id} {path}"), m));
            }
        }
    }
    let leagues = ctx.record_ids(RecordKindV1::LeagueCompetition);
    for &id in leagues.iter().rev().take(12) {
        for (path, n) in [("matches", 2), ("playoffs", 2), ("promotion_series", 1)] {
            for m in sample(&ids_at(ctx, RecordKindV1::LeagueCompetition, id, path), n) {
                picked.push((format!("league_competition {id} {path}"), m));
            }
        }
    }
    let matches: Vec<String> = picked
        .iter()
        .map(|(from, m)| {
            format!("{{\"from\": \"{from}\", \"id\": {m}, \"record\": {}}}",
                    ctx.record_get_json(RecordKindV1::Match, *m, "").unwrap_or_else(|| "null".into()))
        })
        .collect();
    field(&mut out, "matches_sample", &array(&matches));
    out.push_str("\n}\n");
    let path = data_dir().join("league_esports_probe.json");
    std::fs::write(&path, &out)?;
    let summary = format!("{} bytes; {}; {} sample matches", out.len(), counts.join(", "), matches.len());
    Ok((path, summary))
}

// ===================== 服务端钩子 =====================

#[derive(Default)]
struct State {
    probed: bool,
    seq: u64,
}

static STATE: Mutex<Option<State>> = Mutex::new(None);

struct ServerExt;

impl StableServerExtension for ServerExt {
    fn on_server_start(&self, _ctx: &mut StableServerCtx<'_>) {
        // another save: probe it again
        *STATE.lock().unwrap_or_else(PoisonError::into_inner) = None;
        wlog("server start (a save is loading)");
    }

    fn before_management_tick(&self, ctx: &mut StableServerCtx<'_>) {
        let mut guard = STATE.lock().unwrap_or_else(PoisonError::into_inner);
        let st = guard.get_or_insert_with(State::default);
        if !st.probed && !ctx.record_ids(RecordKindV1::YearSchedule).is_empty() {
            st.probed = true;
            match probe(ctx) {
                Ok((path, summary)) => wlog(format!("PROBE written to {}: {summary}", path.display())),
                Err(e) => wlog(format!("PROBE failed: {e}")),
            }
        }
        for ev in ctx.management_events_after(st.seq) {
            st.seq = ev.seq;
            if ev.kind == Some(ManagementEventKindV1::SeasonRollover) {
                wlog(format!("SEASON ROLLOVER #{}: {}", ev.seq, ev.payload_json));
            }
        }
    }
}

fn init(host: &StableHost) -> StableMod {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (League of Legends names for the career's leagues and cups; a read-only probe of its year schedule) \
         loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.set_server_extension(ServerExt);
    host.log(LogLevel::Info, "league_esports loaded (League names, a read-only probe of the year schedule).");
    module
}

declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ints_reads_a_match_list() {
        assert_eq!(ints("[12, 345,6]"), vec![12, 345, 6]);
        assert_eq!(ints("[[1,2],[30]]"), vec![1, 2, 30]);
        assert_eq!(ints("[]"), Vec::<usize>::new());
        assert_eq!(ints("7"), vec![7]);
    }

    #[test]
    fn sample_keeps_the_first_and_the_last() {
        assert_eq!(sample(&[1, 2, 3, 4, 5], 2), vec![1, 2, 5]);
        assert_eq!(sample(&[1, 2], 3), vec![1, 2]);
        assert_eq!(sample(&[], 3), Vec::<usize>::new());
    }

    #[test]
    fn the_probe_document_is_json_shaped() {
        let mut out = String::from("{\n");
        field(&mut out, "a", "1");
        field(&mut out, "b", &array(&["{\"x\": 1}".to_string(), "null".to_string()]));
        out.push_str("\n}\n");
        assert_eq!(out, "{\n\"a\": 1,\n\"b\": [\n{\"x\": 1},\nnull\n]\n}\n");
    }

    #[test]
    fn the_names_cover_every_league_and_cup() {
        let text = include_str!("../text/ui.i18n");
        for key in ["tack", "tacc", "tace", "taca", "tacs", "tacj", "tack2", "tacc2", "tace2", "taca2", "tacs2", "tacj2",
                    "masters", "champions", "challengers_east", "challengers_west"] {
            assert!(text.matches(&format!("\"{key}\":")).count() >= 3, "{key} in every language");
        }
    }
}
