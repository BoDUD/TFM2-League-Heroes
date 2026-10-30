//! The tft pack's own code (tft.dll, next to tft/mod.mod_info): what a tft hero's data cannot do, one module a hero,
//! all in the one tft mod (the user, 2026-10-26: 「诺拉和爆爆合并在一个mod啊」「tft的英雄都放一个mod里 参考英雄联盟」).
//! A new hero: its module here, its `register` called from `init`.

pub mod alune;
pub mod aoshin;
pub mod daeja;
pub mod idas;
pub mod kobuko;
pub mod krug;
pub mod loris;
pub mod maddie;
pub mod nomsy;
pub mod norra;
pub mod renni;
pub mod scar;
pub mod sentinel;
pub mod sevika;
pub mod shiohyu;
pub mod silco;
pub mod smeech;
pub mod sohm;
pub mod steb;
pub mod syfen;
pub mod terra;
pub mod vander;
pub mod violet;

use mod_api_stable::*;

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new("tft");
    alune::register(host, &mut module);
    aoshin::register(host, &mut module);
    daeja::register(host, &mut module);
    idas::register(host, &mut module);
    kobuko::register(host, &mut module);
    krug::register(host, &mut module);
    loris::register(host, &mut module);
    maddie::register(host, &mut module);
    nomsy::register(host, &mut module);
    norra::register(host, &mut module);
    renni::register(host, &mut module);
    scar::register(host, &mut module);
    sentinel::register(host, &mut module);
    sevika::register(host, &mut module);
    shiohyu::register(host, &mut module);
    silco::register(host, &mut module);
    smeech::register(host, &mut module);
    sohm::register(host, &mut module);
    steb::register(host, &mut module);
    syfen::register(host, &mut module);
    terra::register(host, &mut module);
    vander::register(host, &mut module);
    violet::register(host, &mut module);
    module
}

declare_stable_mod!(init, requires = 9);
