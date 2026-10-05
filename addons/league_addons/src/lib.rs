//! 英雄联盟英雄包 附加包合集：全部原生代码附加包放进一个 mod（用户：「那还是做成一个附加包合集」）。
//!
//! 每个附加包仍是 `addons/league_*` 里自己的 crate（单独编译还是它自己的 DLL）；这里把它们的源码当模块编进来，
//! 用 `register` 把各自的原生效果、被动、AI 钩子和地图读取注册到同一个 `StableMod`。名字不变（`league_nocturne_dark:start`
//! 等），所以各附加包的英雄数据原样可用；游戏一个 mod 只加载一个 DLL，两个附加包的 DLL 不能放进同一个文件夹。
//! 数据（英雄副本、文字、特效）由 `assemble.py` 从各附加包的文件夹合成，路径改到 `asset/league_addons/`。
//!
//! 各附加包的日志照旧各写各的（`%APPDATA%\TeamSamoyed\TeamfightManager2\data\<附加包>.log`）。

use mod_api_stable::*;

#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_aatrox_chain/src/lib.rs"]
mod aatrox_chain;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_camille_wall/src/lib.rs"]
mod camille_wall;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_kayn_form/src/lib.rs"]
mod kayn_form;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_leesin_hop/src/lib.rs"]
mod leesin_hop;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nocturne_dark/src/lib.rs"]
mod nocturne_dark;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_tryndamere_rage/src/lib.rs"]
mod tryndamere_rage;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_zilean_rewind/src/lib.rs"]
mod zilean_rewind;

pub const ID: &str = "league_addons";

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    nocturne_dark::register(host, &mut module);
    camille_wall::register(host, &mut module);
    zilean_rewind::register(host, &mut module);
    leesin_hop::register(host, &mut module);
    aatrox_chain::register(host, &mut module);
    kayn_form::register(host, &mut module);
    tryndamere_rage::register(host, &mut module);
    host.log(
        LogLevel::Info,
        "league_addons loaded: Nocturne darkness, Camille wall hook, Zilean true rewind, Lee Sin W dash, Aatrox chain, Kayn forms, Tryndamere low-health rage.",
    );
    module
}

declare_stable_mod!(init, requires = 9);
