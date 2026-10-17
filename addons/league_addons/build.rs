// The add-ons' sources are compiled here as modules: `league_bundle` turns off their own DLL entry points
// (`declare_stable_mod!`), so this crate exports the only one.
fn main() {
    println!("cargo::rustc-check-cfg=cfg(league_bundle)");
    println!("cargo::rustc-cfg=league_bundle");
}
