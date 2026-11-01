// The add-ons' sources are compiled here as modules: `league_bundle` turns off their own DLL entry points
// (`declare_stable_mod!`), so this crate exports the only one.
use std::path::Path;

fn main() {
    println!("cargo::rustc-check-cfg=cfg(league_bundle)");
    // RUSTFLAGS="--cfg ult_press_verify": league_ult_press's self-check build (its look())
    println!("cargo::rustc-check-cfg=cfg(ult_press_verify)");
    println!("cargo::rustc-cfg=league_bundle");
    // Each add-on's own version for its log header (its `VERSION`): compiled in here, its env!("CARGO_PKG_VERSION")
    // would be this crate's 0.1.0 (2026-11-02: the headers of 61 add-ons read v0.1.0, others a stale written-out one), so
    // every add-on gets its mod.mod_info version (what the game shows) as ADDON_VERSION_<id>.
    println!("cargo::rerun-if-changed=build.rs");
    println!("cargo::rerun-if-changed=src/lib.rs");
    let addons = Path::new(&std::env::var("CARGO_MANIFEST_DIR").unwrap()).parent().unwrap().to_path_buf();
    let mut dirs: Vec<_> = std::fs::read_dir(&addons).unwrap().flatten().map(|e| e.path()).collect();
    dirs.sort();
    for dir in dirs {
        let id = dir.file_name().unwrap().to_string_lossy().to_string();
        let info = dir.join("mod.mod_info");
        if !id.starts_with("league_") || id == "league_addons" || !info.is_file() {
            continue;
        }
        println!("cargo::rerun-if-changed={}", info.display());
        if let Some(v) = std::fs::read_to_string(&info).ok().as_deref().and_then(top_version) {
            println!("cargo::rustc-env=ADDON_VERSION_{id}={v}");
        }
    }
}

/// The mod's own "version" in a mod.mod_info: the last one that is a version, not a dependency's requirement (">=0.4.11").
fn top_version(json: &str) -> Option<String> {
    json.match_indices("\"version\"")
        .filter_map(|(i, _)| {
            let rest = json[i + 9..].trim_start().strip_prefix(':')?.trim_start().strip_prefix('"')?;
            let v = &rest[..rest.find('"')?];
            v.starts_with(|c: char| c.is_ascii_digit()).then(|| v.to_string())
        })
        .last()
}
