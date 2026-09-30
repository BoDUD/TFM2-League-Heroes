// Parse TFM2 champion data with the engine's own types (the game's mod SDK ships game_core).
// Only the classic SDK does, and it ended with game 0.5 (game_core 0.5.1 in `mod-sdk`); since 0.6 the game ships
// just the stable-ABI `mod-sdk-stable`, no engine inside - see champion-data section 9 for what that leaves out.
//
//     sdk_probe champ <file.data_champion>    whole kit through game_core::DataChampionInfo
//     sdk_probe effects <file>                one effect JSON per line through game_core::DataEffectDef;
//                                             prints each parsed effect with every field and default,
//                                             or serde's error (an unknown variant lists all accepted ones)
//
// Build once with the SDK's pinned toolchain (the rlibs only load in the rustc that built them):
//
//     set SDK=D:\steam\steamapps\common\Teamfight Manager2\mod-sdk
//     rustup run nightly-2026-05-24 rustc sdk_probe.rs --edition 2021 -o sdk_probe.exe ^
//         -L "dependency=%SDK%\deps" -L "native=%SDK%\native" ^
//         --extern "game_core=%SDK%\deps\libgame_core-ca200d77d5c563ee.rlib" ^
//         --extern "serde_json=%SDK%\deps\libserde_json-aa3421a9f0eb33d2.rlib"
//
// The SDK carries two serde_json builds; the one game_core was not built against fails with
// "the trait bound `DataChampionInfo: Deserialize` is not satisfied". Unknown keys are skipped
// silently, so a field missing from the printed value is one the engine never reads.
extern crate game_core;
extern crate serde_json;

use std::{env, fs, process};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: sdk_probe champ|effects <file>");
        process::exit(2);
    }
    let raw = fs::read_to_string(&args[2]).unwrap_or_else(|e| {
        eprintln!("cannot read {}: {}", args[2], e);
        process::exit(2);
    });
    let raw = raw.trim_start_matches('\u{feff}');
    let mut failed = false;
    if args[1] == "champ" {
        match serde_json::from_str::<game_core::DataChampionInfo>(raw) {
            Ok(_) => println!("OK {}", args[2]),
            Err(e) => {
                println!("ERR {}: {}", args[2], e);
                failed = true;
            }
        }
    } else {
        for (i, line) in raw.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() || line.starts_with("//") {
                continue;
            }
            match serde_json::from_str::<game_core::DataEffectDef>(line) {
                Ok(v) => println!("{}: OK {:?}", i + 1, v),
                Err(e) => {
                    println!("{}: ERR {}", i + 1, e);
                    failed = true;
                }
            }
        }
    }
    process::exit(if failed { 1 } else { 0 });
}
