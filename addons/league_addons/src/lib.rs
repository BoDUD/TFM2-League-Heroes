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
#[path = "../../league_unlock_guard/src/lib.rs"]
mod unlock_guard;
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
#[path = "../../league_caitlyn/src/lib.rs"]
mod caitlyn;
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
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_elise/src/lib.rs"]
mod elise;
#[path = "../../league_katarina/src/lib.rs"]
mod katarina;
#[path = "../../league_shen_shield/src/lib.rs"]
mod shen_shield;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_tahmkench/src/lib.rs"]
mod tahmkench;
#[path = "../../league_kalista/src/lib.rs"]
mod kalista;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_drmundo/src/lib.rs"]
mod drmundo;
#[path = "../../league_pantheon/src/lib.rs"]
mod pantheon;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_orianna/src/lib.rs"]
mod orianna;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_aphelios/src/lib.rs"]
mod aphelios;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_rell/src/lib.rs"]
mod rell;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_urgot/src/lib.rs"]
mod urgot;
#[path = "../../league_reksai/src/lib.rs"]
mod reksai;
#[path = "../../league_ult_press/src/lib.rs"]
mod ult_press;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_yunara/src/lib.rs"]
mod yunara;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_swain/src/lib.rs"]
mod swain;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_renata/src/lib.rs"]
mod renata;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_nasus/src/lib.rs"]
mod nasus;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_anivia/src/lib.rs"]
mod anivia;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_jarvaniv/src/lib.rs"]
mod jarvaniv;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_ziggs/src/lib.rs"]
mod ziggs;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_maokai/src/lib.rs"]
mod maokai;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_gangplank/src/lib.rs"]
mod gangplank;
#[path = "../../league_wukong/src/lib.rs"]
mod wukong;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_cassiopeia/src/lib.rs"]
mod cassiopeia;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_akshan/src/lib.rs"]
mod akshan;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_poppy/src/lib.rs"]
mod poppy;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_volibear/src/lib.rs"]
mod volibear;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_rammus/src/lib.rs"]
mod rammus;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_zoe/src/lib.rs"]
mod zoe;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_yuumi/src/lib.rs"]
mod yuumi;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_quinn/src/lib.rs"]
mod quinn;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_chogath/src/lib.rs"]
mod chogath;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_karthus/src/lib.rs"]
mod karthus;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_vex/src/lib.rs"]
mod vex;
#[path = "../../league_zyra/src/lib.rs"]
mod zyra;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_graves/src/lib.rs"]
mod graves;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_warwick/src/lib.rs"]
mod warwick;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_mel/src/lib.rs"]
mod mel;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_gnar/src/lib.rs"]
mod gnar;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_sylas/src/lib.rs"]
mod sylas;
#[path = "../../league_velkoz/src/lib.rs"]
mod velkoz;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_ornn/src/lib.rs"]
mod ornn;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_naafiri/src/lib.rs"]
mod naafiri;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_heimerdinger/src/lib.rs"]
mod heimerdinger;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_neeko/src/lib.rs"]
mod neeko;
#[path = "../../league_ksante/src/lib.rs"]
mod ksante;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_udyr/src/lib.rs"]
mod udyr;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_qiyana/src/lib.rs"]
mod qiyana;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_ivern/src/lib.rs"]
mod ivern;
#[allow(dead_code)] // items public in the add-on's own crate
#[path = "../../league_illaoi/src/lib.rs"]
mod illaoi;

pub const ID: &str = "league_addons";

/// A mod has one map hook: Camille's wall reader, Rengar's, Nidalee's and Maokai's bush readers and Qiyana's terrain
/// reader all read the map's document.
struct MapReaders;
impl StableMapCustomizer for MapReaders {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        camille_wall::WallReader.customize(mode, doc);
        rengar_bush::BushReader::read(mode, doc);
        nidalee::bush::BushReader::read(mode, doc);
        maokai::bush::BushReader::read(mode, doc);
        qiyana::terrain::TerrainReader::read(mode, doc);
    }
}

/// A mod has one client extension slot (set_extension keeps only the last): Viego's ClockReader (the screen's match
/// clock for his possession, fed to game_places::clock for Neeko's disguise and Akshan's banner) and Akshan's revive
/// banner drawn over the screen. Set after every register, so it replaces the ClockReader viego_soul::register sets.
struct BundleClient;
impl StableExtension for BundleClient {
    fn post_update(&self, ctx: &mut StableClient<'_>, dt: u64) {
        viego_soul::view::ClockReader.post_update(ctx, dt);
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        akshan::banner::draw(ctx);
    }
}

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    // its hook runs after every other one whatever the order here (the top priority): a skill2 / ult still
    // level-locked in the final input becomes an attack or a stand (league_unlock_guard/README.md)
    unlock_guard::register(host, &mut module);
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
    // Viego sets his ClockReader as the client extension; BundleClient (set at the end) replaces it and calls it, with
    // Akshan's banner: an add-on that needs the client extension goes into BundleClient (game_places/src/clock.rs)
    viego_soul::register(host, &mut module);
    zeri::register(host, &mut module);
    nautilus::register(host, &mut module);
    darius_ult::register(host, &mut module);
    caitlyn::register(host, &mut module);
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
    elise::register(host, &mut module);
    katarina::register(host, &mut module);
    shen_shield::register(host, &mut module);
    tahmkench::register(host, &mut module);
    kalista::register(host, &mut module);
    drmundo::register(host, &mut module);
    pantheon::register(host, &mut module);
    orianna::register(host, &mut module);
    aphelios::register(host, &mut module);
    rell::register(host, &mut module);
    urgot::register(host, &mut module);
    reksai::register(host, &mut module);
    ult_press::register(host, &mut module);
    yunara::register(host, &mut module);
    swain::register(host, &mut module);
    renata::register(host, &mut module);
    nasus::register(host, &mut module);
    anivia::register(host, &mut module);
    jarvaniv::register(host, &mut module);
    ziggs::register(host, &mut module);
    maokai::register(host, &mut module);
    gangplank::register(host, &mut module);
    wukong::register(host, &mut module);
    cassiopeia::register(host, &mut module);
    akshan::register(host, &mut module);
    poppy::register(host, &mut module);
    volibear::register(host, &mut module);
    rammus::register(host, &mut module);
    zoe::register(host, &mut module);
    yuumi::register(host, &mut module);
    quinn::register(host, &mut module);
    chogath::register(host, &mut module);
    karthus::register(host, &mut module);
    vex::register(host, &mut module);
    zyra::register(host, &mut module);
    graves::register(host, &mut module);
    warwick::register(host, &mut module);
    mel::register(host, &mut module);
    gnar::register(host, &mut module);
    sylas::register(host, &mut module);
    velkoz::register(host, &mut module);
    ornn::register(host, &mut module);
    naafiri::register(host, &mut module);
    heimerdinger::register(host, &mut module);
    neeko::register(host, &mut module);
    ksante::register(host, &mut module);
    udyr::register(host, &mut module);
    qiyana::register(host, &mut module);
    ivern::register(host, &mut module);
    illaoi::register(host, &mut module);
    module.set_map_customizer(MapReaders);
    module.set_extension(BundleClient);
    host.log(
        LogLevel::Info,
        "league_addons loaded: Nocturne darkness, Camille wall hook, Zilean true rewind, Lee Sin W dash, Aatrox chain, Kayn forms, Tryndamere low-health rage, Xin Zhao far-damage guard, Pyke exact execute, Kha'Zix vision and evolutions, Gwen % max-health magic cuts, Fiora's Grand Challenge Vitals, Vayne's Silver Bolts per target, Brand Blaze stacks on each enemy, Renekton's Fury below half health, Lillia's Dream Dust magic and a sleep that breaks on damage, Kayle's ascension kept through death, Vladimir's Sanguine Pool at low health, Rengar's leap from the map's bushes, Zed's Contempt and Death Mark from health and damage, Olaf's Berserker Rage from missing health, Talon's Assassin's Path over walls, Senna's Mist and Veigar's ability power kept through death, Syndra's W lifting minions and monsters, Viego's possession, Zeri's wall laser and shield steal, Nautilus's Dredge Line hooking walls, Darius's Noxian Guillotine only for a kill, Caitlyn's early lane pressure (Q and shots at the enemy laner), Gragas's Explosive Cask aimed behind the enemies, Irelia's Bladesurge resets and wave hops, Kassadin's exact Void Stone, Force Pulse charged by casts nearby and Riftwalk's landing, Corki's missiles aimed and Valkyrie escapes, Braum's Concussive Blows per champion (allies' attacks too), Unbreakable from the shield's side and Glacial Fissure's line, Mordekaiser's Realm of Death duel and Indestructible from the damage, Nidalee's whole-body cougar, Prowl in brush and her javelin's and hunt pounce's targets, Galio's Shield of Durand after 12 s untouched, its taunt by the champions near and Hero's Entrance beside the ally in the worst fight, Nilah's Joy Unending heals and shields, Jubilant Veil when struck and Apotheosis's timing, Bard's smart Magical Journey clear of walls, Sion's Glory in Death zombie and Soul Furnace from every kill, Kindred's Lamb's Respite only to save someone about to die, Malzahar's Void Shift as in League and Malefic Visions jumping on every death, Smolder's stacks kept through death, his tier-3 execute and Flap over walls, Milio's Fired Up! burning on an ally's next hit and Breath of Life only to save, with a real cleanse, a read-only recall log, Jayce's whole-body cannon, Thundering Blow toward his side and the smart gate shot, Elise's whole-body spider and her Cocoon's, Rappel's and hunt's targets, Katarina's smart Shunpo onto her daggers with Voracity on every takedown, Shen's ult shield from his maximum health, Tahm Kench's An Acquired Taste per champion, real grey health, Devour saving the ally in danger and Abyssal Dive only with allies beside him, Kalista's hop forward or back, her Oathsworn hurled by Fate's Call and Rend's execute, Dr. Mundo's real block of the first hard crowd control, Infected Bonesaw by current health, Blunt Force Trauma by missing health, Heart Zapper's real grey health and Maximum Dosage when his health runs low, Pantheon's Aegis Assault blocking the front only, Comet Spear's execute and Grand Starfall's spot, Orianna's Ball flying from where it is, Command: Protect to the ally in danger and Command: Shockwave for a kill, Aphelios's whole-body weapon forms, League's weapon queue and Severum when low, Rell's whole body on foot, Break the Mold per champion, shield-breaking Shattering Strike and Full Tilt toward, and Rek'Sai's burrowed body, tunnels and Void Rush by real health, Urgot's Echoing Flames by direction and Fear Beyond Death's real execute, Swain's Soul Fragments kept through death and his whole-body demon, Nasus's Siphoning Strike stacks kept through death, Fury of the Sands halving Q only and his whole big body, and Yunara's Untouchable Shadow toward or away, Kanmei's Steps faster toward a champion, Transcend One's Self by real health and her Transcendent body, Renata's Leverage popped by her allies' hits, League's Bailout and a real berserk, and Anivia's Rebirth egg (on lethal damage, its cooldown kept through death), a real Crystallize wall and Frostbite doubled on Iced targets, Jarvan IV's real Cataclysm rock ring, Ziggs's Satchel Charge hexploding low towers with Short Fuse x1.75 on towers, Maokai's Sap Magic healing % max health (readied by enemy skills too) with saplings bursting bigger in brush, and Gangplank's Remove Scurvy cleansing (also eaten at low health) with Powder Kegs chaining, Wukong's Stone Skin regenerating % max health, Cassiopeia's Twin Fang on the poisoned target with Petrifying Gaze by facing, Akshan's Dirty Fighting per target, Comeuppance from missing health and his Scoundrels' victims revived (with a banner on screen), and Poppy's Steadfast Presence stopping dashes, Heroic Charge stunning on walls and Keeper's Verdict sending champions toward their fountain, and Volibear's chain lightning to the 4 nearest, Frenzied Maul's mark kept on the champion bitten and Stormbringer silencing towers, Rammus's rolling Powerball and spiked shell, and Zoe's sleep broken by damage, Paddle Star by the distance flown and Spell Thief's shards, Yuumi riding her ally with no time limit, untargetable, casting from his head Quinn's ride on Valor with Skystrike when it runs out Cho'Gath's Feast stacks kept through death with Feast only for a kill, Karthus's Death Defied spirit, Vex's Gloom on each enemy (dashes too) with Shadow Surge's reset and Zyra's seeds on the ground growing plants that strike champions first, and Graves's Quickdraw cooldown per pellet, pellet knockback, Collateral Damage's cone and his combos (Quickdraw after the first shell, Collateral Damage for a kill), and Warwick's Eternal Hunger and Blood Hunt by health with his combos (Primal Howl before Jaws of the Beast, Jaws after Infinite Duress, Infinite Duress at a champion under a quarter), and Sylas's Hijack by the robbed champion's class with Kingslayer by missing health and his combos (Chain Lash after Abduct, the stolen ultimate kept for two champions or a wounded one), and Mel's Overwhelm execute and Rebuttal sending enemy projectiles back with her combos (Solar Snare before Radiant Volley, Golden Eclipse only for a kill or two champions stacked), and Ornn's real magma pillar, quakes on pillars and walls, Brittle per champion, Living Forge raising every item's stats and his combos (the pillar before the charge, a champion beside the pillar charged, Brittle champions hit first), and Naafiri's second dagger executing by missing health, Hounds' Pursuit again on every takedown, a smart ult and four hounds in the roar, and Heimerdinger's turrets firing visible shots from their muzzles with Hextech Affinity by his side's towers too, Neeko's disguise as an ally, K'Sante's All Out body, and Udyr's Iron Mantle by health with his whole-body stances, Qiyana's elements by the terrain beside her (else by the situation), Royal Privilege per enemy and her rock execute, and Ivern's Brushmaker brush as a real brush (Rengar pounces from it, Qiyana takes grass from it), and Illaoi's tentacles on the walls' edges striking the lessoned and Vessels first, with Test of Spirit's echo and leash.",
    );
    module
}

declare_stable_mod!(init, requires = 9);
