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
#[path = "../../league_brand/src/lib.rs"]
mod brand;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_camille_wall/src/lib.rs"]
mod camille_wall;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_fiora_duel/src/lib.rs"]
mod fiora_duel;
#[path = "../../league_gwen/src/lib.rs"]
mod gwen;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_kayle/src/lib.rs"]
mod kayle;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_kayn_form/src/lib.rs"]
mod kayn_form;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_khazix/src/lib.rs"]
mod khazix;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_leesin_hop/src/lib.rs"]
mod leesin_hop;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_lillia/src/lib.rs"]
mod lillia;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nocturne_dark/src/lib.rs"]
mod nocturne_dark;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_pyke/src/lib.rs"]
mod pyke;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_rengar_bush/src/lib.rs"]
mod rengar_bush;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_renekton/src/lib.rs"]
mod renekton;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_tryndamere_rage/src/lib.rs"]
mod tryndamere_rage;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_vayne_bolts/src/lib.rs"]
mod vayne_bolts;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_vladimir_pool/src/lib.rs"]
mod vladimir_pool;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_xinzhao_guard/src/lib.rs"]
mod xinzhao_guard;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_zilean_rewind/src/lib.rs"]
mod zilean_rewind;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_zed_mark/src/lib.rs"]
mod zed_mark;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_olaf_rage/src/lib.rs"]
mod olaf_rage;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_talon_vault/src/lib.rs"]
mod talon_vault;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_senna_mist/src/lib.rs"]
mod senna_mist;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_veigar_power/src/lib.rs"]
mod veigar_power;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_syndra/src/lib.rs"]
mod syndra;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_viego_soul/src/lib.rs"]
mod viego_soul;
#[path = "../../league_zeri/src/lib.rs"]
mod zeri;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nautilus/src/lib.rs"]
mod nautilus;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_darius_ult/src/lib.rs"]
mod darius_ult;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_gragas/src/lib.rs"]
mod gragas;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_irelia/src/lib.rs"]
mod irelia;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_kassadin/src/lib.rs"]
mod kassadin;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_corki/src/lib.rs"]
mod corki;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_braum/src/lib.rs"]
mod braum;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_mordekaiser/src/lib.rs"]
mod mordekaiser;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nidalee/src/lib.rs"]
mod nidalee;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_galio/src/lib.rs"]
mod galio;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nilah/src/lib.rs"]
mod nilah;
#[path = "../../league_bard/src/lib.rs"]
mod bard;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_sion/src/lib.rs"]
mod sion;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_kindred/src/lib.rs"]
mod kindred;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_malzahar/src/lib.rs"]
mod malzahar;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_smolder/src/lib.rs"]
mod smolder;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_milio/src/lib.rs"]
mod milio;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_recall_log/src/lib.rs"]
mod recall_log;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_jayce/src/lib.rs"]
mod jayce;

pub const ID: &str = "league_addons";

/// A mod has one map hook: Camille's wall reader and Rengar's and Nidalee's bush readers all read the map's document.
struct MapReaders;
impl StableMapCustomizer for MapReaders {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        camille_wall::WallReader.customize(mode, doc);
        rengar_bush::BushReader::read(mode, doc);
        nidalee::bush::BushReader::read(mode, doc);
    }
}

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    nocturne_dark::register(host, &mut module);
    camille_wall::register(host, &mut module);
    zilean_rewind::register(host, &mut module);
    leesin_hop::register(host, &mut module);
    aatrox_chain::register(host, &mut module);
    kayn_form::register(host, &mut module);
    tryndamere_rage::register(host, &mut module);
    xinzhao_guard::register(host, &mut module);
    pyke::register(host, &mut module);
    khazix::register(host, &mut module);
    gwen::register(host, &mut module);
    fiora_duel::register(host, &mut module);
    vayne_bolts::register(host, &mut module);
    brand::register(host, &mut module);
    renekton::register(host, &mut module);
    lillia::register(host, &mut module);
    kayle::register(host, &mut module);
    vladimir_pool::register(host, &mut module);
    rengar_bush::register(host, &mut module);
    zed_mark::register(host, &mut module);
    olaf_rage::register(host, &mut module);
    talon_vault::register(host, &mut module);
    senna_mist::register(host, &mut module);
    veigar_power::register(host, &mut module);
    syndra::register(host, &mut module);
    viego_soul::register(host, &mut module);
    zeri::register(host, &mut module);
    nautilus::register(host, &mut module);
    darius_ult::register(host, &mut module);
    gragas::register(host, &mut module);
    irelia::register(host, &mut module);
    kassadin::register(host, &mut module);
    corki::register(host, &mut module);
    braum::register(host, &mut module);
    mordekaiser::register(host, &mut module);
    nidalee::register(host, &mut module);
    galio::register(host, &mut module);
    nilah::register(host, &mut module);
    bard::register(host, &mut module);
    sion::register(host, &mut module);
    kindred::register(host, &mut module);
    malzahar::register(host, &mut module);
    smolder::register(host, &mut module);
    milio::register(host, &mut module);
    recall_log::register(host, &mut module);
    jayce::register(host, &mut module);
    module.set_map_customizer(MapReaders);
    host.log(
        LogLevel::Info,
        "league_addons loaded: Nocturne darkness, Camille wall hook, Zilean true rewind, Lee Sin W dash, Aatrox chain, Kayn forms, Tryndamere low-health rage, Xin Zhao far-damage guard, Pyke exact execute, Kha'Zix vision and evolutions, Gwen % max-health magic cuts, Fiora's Grand Challenge Vitals, Vayne's Silver Bolts per target, Brand Blaze stacks on each enemy, Renekton's Fury below half health, Lillia's Dream Dust magic and a sleep that breaks on damage, Kayle's ascension kept through death, Vladimir's Sanguine Pool at low health, Rengar's leap from the map's bushes, Zed's Contempt and Death Mark from health and damage, Olaf's Berserker Rage from missing health, Talon's Assassin's Path over walls, Senna's Mist and Veigar's ability power kept through death, Syndra's W lifting minions and monsters, Viego's possession, Zeri's wall laser and shield steal, Nautilus's Dredge Line hooking walls, Darius's Noxian Guillotine only for a kill or under Noxian Might, Gragas's Explosive Cask aimed behind the enemies, Irelia's Bladesurge resets and wave hops, Kassadin's exact Void Stone, Force Pulse charged by casts nearby and Riftwalk's landing, Corki's missiles aimed and Valkyrie escapes, Braum's Concussive Blows per champion (allies' attacks too), Unbreakable from the shield's side and Glacial Fissure's line, Mordekaiser's Realm of Death duel and Indestructible from the damage, Nidalee's whole-body cougar, Prowl in brush and her javelin's and hunt pounce's targets, Galio's Shield of Durand after 12 s untouched, its taunt by the champions near and Hero's Entrance beside the ally in the worst fight, Nilah's Joy Unending heals and shields, Jubilant Veil when struck and Apotheosis's timing, Bard's smart Magical Journey clear of walls, Sion's Glory in Death zombie and Soul Furnace from every kill, Kindred's Lamb's Respite only to save someone about to die, Malzahar's Void Shift as in League and Malefic Visions jumping on every death, Smolder's stacks kept through death, his tier-3 execute and Flap over walls, Milio's Fired Up! burning on an ally's next hit and Breath of Life only to save, with a real cleanse, a read-only recall log, and Jayce's whole-body cannon, Thundering Blow toward his side and the smart gate shot.",
    );
    module
}

declare_stable_mod!(init, requires = 9);
