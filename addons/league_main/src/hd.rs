//! Which of the main pack's heroes have dense (PPU) frames: league.dll's table (the tft pack's rows are in
//! tft/src/hd.rs since 2026-10-31). What a row does is hd_engine's (addons/hd_engine: src/hd.rs Table, src/lookup.rs,
//! src/view.rs, src/ui.rs); league.dll hands it this table at init (src/lib.rs) - hooking the game itself when it is
//! the first pack DLL loaded, else handing the table to the one that did (tft.dll, hd_engine src/share.rs).
//!
//! A hero listed in `HEROES` carries `hd_<tag>` beside every `<tag>` in its own sheet (tools/art/ppu_hd.py, the same
//! PPU there), each frame PPU times the 1x frame's size - a drawn one may be grown alike at both ends (its centre, the
//! pivot, kept), hd_idle exactly PPU times as wide (hd_engine src/lookup.rs tells a changed table by it). The tags are
//! read from the sheet's .fanim compiled in.

use hd_engine::Table;

/// Champion id, pixels per 1x square, the sheet's .fanim (as shipped in league/).
pub const HEROES: &[(&str, f32, &str)] = &[
    ("league_yasuo", 2.2, include_str!("../../../league/champions/league_yasuo#anim.fanim")),
    ("league_gragas", 1.45, include_str!("../../../league/champions/league_gragas#anim.fanim")),
    ("league_zeri", 3.0, include_str!("../../../league/champions/league_zeri#anim.fanim")),
    ("league_vladimir", 1.8, include_str!("../../../league/champions/league_vladimir#anim.fanim")),
    ("league_karma", 2.2, include_str!("../../../league/champions/league_karma#anim.fanim")),
    ("league_ashe", 2.2, include_str!("../../../league/champions/league_ashe#anim.fanim")),
    ("league_irelia", 2.0, include_str!("../../../league/champions/league_irelia#anim.fanim")),
    ("league_kassadin", 2.42, include_str!("../../../league/champions/league_kassadin#anim.fanim")),
    ("league_corki", 2.2, include_str!("../../../league/champions/league_corki#anim.fanim")),
    ("league_garen", 1.9, include_str!("../../../league/champions/league_garen#anim.fanim")),
    ("league_braum", 1.98, include_str!("../../../league/champions/league_braum#anim.fanim")),
    ("league_mordekaiser", 2.0, include_str!("../../../league/champions/league_mordekaiser#anim.fanim")),
    ("league_soraka", 2.2, include_str!("../../../league/champions/league_soraka#anim.fanim")),
    ("league_nidalee", 2.2, include_str!("../../../league/champions/league_nidalee#anim.fanim")),
    ("league_galio", 1.65, include_str!("../../../league/champions/league_galio#anim.fanim")),
    ("league_nilah", 1.98, include_str!("../../../league/champions/league_nilah#anim.fanim")),
    ("league_kindred", 2.2, include_str!("../../../league/champions/league_kindred#anim.fanim")),
    ("league_malzahar", 1.38, include_str!("../../../league/champions/league_malzahar#anim.fanim")),
    // Smolder: PPU 1.5 (the user's pick), drawn at 85 % in his design itself (「感觉太大 得缩小一点」), so no SIZES row
    ("league_smolder", 1.5, include_str!("../../../league/champions/league_smolder#anim.fanim")),
    ("league_milio", 2.2, include_str!("../../../league/champions/league_milio#anim.fanim")),
    ("league_jayce", 1.5, include_str!("../../../league/champions/league_jayce#anim.fanim")),
    ("league_elise", 1.8, include_str!("../../../league/champions/league_elise#anim.fanim")),
    ("league_katarina", 1.5, include_str!("../../../league/champions/league_katarina#anim.fanim")),
    ("league_tahmkench", 1.2, include_str!("../../../league/champions/league_tahmkench#anim.fanim")),
    // Kalista: PPU 1.4 (the user's pick), drawn at 85 % in her frames themselves (「大小 85%，PPU 1.4」), so no SIZES row
    ("league_kalista", 1.4, include_str!("../../../league/champions/league_kalista#anim.fanim")),
    // Dr. Mundo: PPU 1.5 (the user's pick, 42 game rows hair to soles)
    ("league_drmundo", 1.5, include_str!("../../../league/champions/league_drmundo#anim.fanim")),
    // Pantheon: PPU 1.5 (the user's pick), his strips drawn at that density on the design's grid, so no SIZES row
    ("league_pantheon", 1.5, include_str!("../../../league/champions/league_pantheon#anim.fanim")),
    // Orianna: PPU 2.25 - the chibi redesign (2026-10-22, 「我要的是Q版的」) is 86 squares bun to soles where the old
    // design had 84 at 2.2, so she stands as tall as before; posed by tools/art/rig_orianna.py on that grid, no SIZES row
    ("league_orianna", 2.25, include_str!("../../../league/champions/league_orianna#anim.fanim")),
    // Aphelios: PPU 1.5 (the user's pick), posed from the design's own squares at that density; 90 % (SIZES, the user:
    // 「厄斐琉斯模型是不是在游戏里太大了？」 then 「缩到 90%」 from a sheet: 47 px against the ADCs' 36-45)
    ("league_aphelios", 1.5, include_str!("../../../league/champions/league_aphelios#anim.fanim")),
    // Rell: PPU 1.5 (the user's pick), posed by tools/art/rig_rell.py on that grid (mounted 44 game rows, on foot 40), so no
    // SIZES row
    ("league_rell", 1.5, include_str!("../../../league/champions/league_rell#anim.fanim")),
    // Rek'Sai: Codex's step-1 takes read back square for square (A 57 rows = the user's 36 game px), posed by
    // tools/art/rig_reksai.py on that grid (57 / 36 = 1.58), pixelated to 1.2 by ppu_restyle (the user: 「雷克赛像素太高
    // 需要降低」, picked 1.2); no SIZES row
    ("league_reksai", 1.2, include_str!("../../../league/champions/league_reksai#anim.fanim")),
    // Urgot: posed at 1.5 squares a game pixel by tools/art/rig_urgot.py (「炮顶到腿尖 42 px，PPU 1.5」), brought to 1.2 by
    // ppu_restyle after the user saw him in game (「现在像素太高 要降低点」 -> 「1.2」); the size unchanged, so no SIZES row
    ("league_urgot", 1.2, include_str!("../../../league/champions/league_urgot#anim.fanim")),
    // Swain: posed by tools/art/rig_swain.py at the user's 1.5 squares a game pixel (40 game rows hair to soles; the demon
    // form's tags on the same body), so no SIZES row
    ("league_swain", 1.5, include_str!("../../../league/champions/league_swain#anim.fanim")),
    // Renata: posed by tools/art/rig_renata.py at the user's 1.5 squares a game pixel (36 game rows hair to soles; the R
    // machine in her own ult frames), so no SIZES row
    ("league_renata", 1.5, include_str!("../../../league/champions/league_renata#anim.fanim")),
    // Nasus: posed by tools/art/rig_nasus.py at the user's 1.2 squares a game pixel (44 game rows ear tips to soles; the big
    // body of Fury of the Sands its own design, 59 rows), so no SIZES row
    ("league_nasus", 1.2, include_str!("../../../league/champions/league_nasus#anim.fanim")),
    // Anivia: posed by tools/art/rig_anivia.py at the user's 1.2 squares a game pixel (38 game rows crown to the lowest
    // wing tip; the Rebirth egg half of that, its own tags), so no SIZES row
    ("league_anivia", 1.2, include_str!("../../../league/champions/league_anivia#anim.fanim")),
    // Jarvan IV: posed by tools/art/rig_jarvaniv.py at the user's 1.5 squares a game pixel (40 game rows helmet to soles,
    // the lance above), so no SIZES row
    ("league_jarvaniv", 1.5, include_str!("../../../league/champions/league_jarvaniv#anim.fanim")),
    // Ziggs: posed by tools/art/rig_ziggs.py at 1.5 squares a game pixel (32 game rows helmet to soles, the bombs held
    // out wide), brought to the user's 1.2 by ppu_restyle (「太高清了 降低点像素」), so no SIZES row
    ("league_ziggs", 1.2, include_str!("../../../league/champions/league_ziggs#anim.fanim")),
    // Maokai: posed by tools/art/rig_maokai.py at 1.5 squares a game pixel (40 game rows crown to the root feet; the
    // user's 「太模糊了 PPU调整一下像素」 raised it from 1.2), brought to the user's 1.3 by ppu_restyle (「太高清了 降低点像素」
    // -> 「1.3吧」), so no SIZES row
    ("league_maokai", 1.3, include_str!("../../../league/champions/league_maokai#anim.fanim")),
    // Gangplank: posed by tools/art/rig_gangplank.py at the user's 1.5 squares a game pixel (41 game rows hat to soles:
    // Codex's step-1 take read back uncut - 「PPU 用 1.5」), Q / R from Codex's gun-hand poses, so no SIZES row
    ("league_gangplank", 1.5, include_str!("../../../league/champions/league_gangplank#anim.fanim")),
    // Wukong: posed by tools/art/rig_wukong.py at the user's 1.5 squares a game pixel (38 game rows hair to soles, the
    // tail and the staff above; 「起码PPU1.5」), so no SIZES row; Codex's actions (rig_frames_1018.py, 1.53) brought to 1.2
    // on 2026-10-18 (「船长猴子阿克尚波比蛇女像素太高需要降低」), back to 1.53 as drawn on 2026-10-29 (「局内模型眼睛细节太差
    // 了」「你不如调高一点PPU像素」「用 1.53」: at 1.2 the eye's single green square was lost, a black band over the face)
    ("league_wukong", 1.53, include_str!("../../../league/champions/league_wukong#anim.fanim")),
    // Cassiopeia: posed by tools/art/rig_cassiopeia.py at the user's 1.3 squares a game pixel (44 game rows crest to the
    // ground: 「44 ppu1.3 A」), so no SIZES row
    ("league_cassiopeia", 1.2, include_str!("../../../league/champions/league_cassiopeia#anim.fanim")),
    // Akshan: posed by tools/art/rig_akshan.py at the user's 1.5 squares a game pixel (38 game rows hair to soles, the
    // raised gun above; 「用 A，游戏里 38 像素高，PPU 1.5」), the aim arm and the walk from Codex on the same grid, so no SIZES row
    ("league_akshan", 1.2, include_str!("../../../league/champions/league_akshan#anim.fanim")),
    // Poppy: posed by tools/art/rig_poppy.py at the user's 1.3 squares a game pixel (36 game rows pigtails to soles, the
    // hammer's haft above: 「游戏里 36 像素高，PPU 1.3」); 85 % (SIZES, the user: 「波比在游戏里体型也太大 需要缩小」 - 44 px
    // with the standing hammer against the yordles' 32-40), her frames lowered 2 squares by the restyle (RESTYLE poppy lift_sq)
    ("league_poppy", 1.2, include_str!("../../../league/champions/league_poppy#anim.fanim")),
    // Volibear: posed by tools/art/rig_volibear.py at the user's 1.2 squares a game pixel (44 game rows ear top to soles:
    // 「44 像素，PPU 1.2」), the arm poses, the walk and Q from Codex on the same grid, so no SIZES row
    ("league_volibear", 1.2, include_str!("../../../league/champions/league_volibear#anim.fanim")),
    // Rammus: posed by tools/art/rig_rammus.py from Codex's step-1 takes at the user's 1.2 squares a game pixel (36 game rows
    // spike tips to soles: 「36 像素」「PPU 1.2」; the ball b_* and curl c_* tags the add-on swaps in), so no SIZES row
    ("league_rammus", 1.2, include_str!("../../../league/champions/league_rammus#anim.fanim")),
    // Zoe: posed by tools/art/rig_zoe.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (35 game rows
    // crown to soles: 「35 像素」「PPU 1.5」; skill_w / ult_exit / ult_back the kit's CasterAnimations), so no SIZES row
    ("league_zoe", 1.5, include_str!("../../../league/champions/league_zoe#anim.fanim")),
    // Yuumi: posed by tools/art/rig_yuumi.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (48 game rows
    // orb top to the book's bottom: 「32 像素」「PPU 1.5」), shown at 75 % (SIZES; 「还有模型太大」 -> 「75%（24 像素）」), her frames
    // lowered 6 squares by the restyle (RESTYLE yuumi lift_sq)
    ("league_yuumi", 1.5, include_str!("../../../league/champions/league_yuumi#anim.fanim")),
    // Quinn: posed by tools/art/rig_quinn.py from Codex's redraw of the user's picks at 2.0 squares a game pixel (38 game
    // rows crest to soles: 「38 像素」, then 「像素有点太低了 太多模糊的了 调一下PPU」; her legs drawn on League's bones; the
    // ride r_* tags the add-on swaps in), so no SIZES row
    ("league_quinn", 2.0, include_str!("../../../league/champions/league_quinn#anim.fanim")),
    // Cho'Gath: posed by tools/art/rig_chogath.py at the user's 1.2 squares a game pixel (「38 像素」「PPU 1.2」: Codex's step-1
    // take A-1 cut to 46 rows, the side view redrawn on the grid, Codex's action poses read back at its scale with the
    // idle's head), so no SIZES row; Feast's stacks draw his body bigger (GROWTH)
    ("league_chogath", 1.2, include_str!("../../../league/champions/league_chogath#anim.fanim")),
    // Karthus: posed by tools/art/rig_karthus.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (40 game
    // rows crown to soles: 「40 像素，PPU 1.5」; attack_w is Wall of Pain's cast in the attack, ult the 3 s Requiem), so no
    // SIZES row
    ("league_karthus", 1.5, include_str!("../../../league/champions/league_karthus#anim.fanim")),
    // Vex: posed by tools/art/rig_vex.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (63 game rows from
    // her Shadow's ear tips to her soles, her own 51: 「34 像素」「PPU 1.5」; ult_dash / ult_hit the kit's CasterAnimations),
    // so no SIZES row
    ("league_vex", 1.5, include_str!("../../../league/champions/league_vex#anim.fanim")),
    // Zyra: posed by tools/art/rig_zyra.py on Codex's step-1 take A-1 at 1.7 squares a game pixel (74 game rows hair to
    // soles, her own face: 「提高点ppu像素吧」「脸部完全变形了啊」; every action on the 3/4 design: 「就用四分之三面来做啊」), so no
    // SIZES row
    ("league_zyra", 1.7, include_str!("../../../league/champions/league_zyra#anim.fanim")),
    // Graves: posed by tools/art/rig_graves.py at the user's 1.5 squares a game pixel (57 game rows hair to soles: 「38 像素」
    // 「PPU 1.5」; Codex's seven poses on skeletons, attack2 the second shell's reload), so no SIZES row
    ("league_graves", 1.5, include_str!("../../../league/champions/league_graves#anim.fanim")),
    // Warwick: posed by tools/art/rig_warwick.py on Codex's step-1 take A-1 at the user's 1.5 squares a game pixel (69 game
    // rows spike top to soles: 「选大一号的那个」「PPU 1.5」; every action on the 3/4 design: 「不做侧面 只做四分之三的侧面」;
    // skill_bite / skill2_howl / ult_dash / ult_hold the kit's CasterAnimations), brought down to 1.2 by ppu_restyle
    // (「太高清了 降点像素」), so no SIZES row
    ("league_warwick", 1.2, include_str!("../../../league/champions/league_warwick#anim.fanim")),
    // Gnar: posed by tools/art/rig_gnar.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (Mini 48 game
    // rows skull cap to soles, Mega 66: 「迷你 32」「巨型 44」; Mega's m_* tags the kit's CasterAnimations and the add-on's
    // whole-body swap), so no SIZES row
    ("league_gnar", 1.5, include_str!("../../../league/champions/league_gnar#anim.fanim")),
    // Sylas: posed by tools/art/rig_sylas.py at the user's 1.2 squares a game pixel (46 game rows hair to soles: 「38」
    // 「PPU 1.2」; 3/4 only, Codex's sixteen skeleton poses with the design's head; attack_p / skill_w / skill2_pull /
    // ult_cast / ult_dash the kit's CasterAnimations), so no SIZES row
    ("league_sylas", 1.2, include_str!("../../../league/champions/league_sylas#anim.fanim")),
    // Mel: posed by tools/art/rig_mel.py on Codex's step-1 take A-3 at the user's 1.5 squares a game pixel (65 game rows bun
    // top to soles: 「44」「PPU 1.5」; every action on the 3/4 design after League's clips), so no SIZES row
    ("league_mel", 1.5, include_str!("../../../league/champions/league_mel#anim.fanim")),
    // Vel'Koz: posed by tools/art/rig_velkoz.py on Codex's step-1 take A-2 at the user's 1.5 squares a game pixel (54 game
    // rows crest top to the lowest tentacle: 「36」「PPU 1.5」; 3/4 only, every action after League's clips; ult_loop the
    // kit's channel CasterAnimation), so no SIZES row
    ("league_velkoz", 1.5, include_str!("../../../league/champions/league_velkoz#anim.fanim")),
    // Ornn: posed by tools/art/rig_ornn.py on Codex's step-1 take A-3 at the user's 1.5 squares a game pixel (66 game rows
    // horn top to soles: 「44」「PPU 1.5」; 3/4 only, Codex's eighteen skeleton poses with the design's face; skill_w /
    // skill2_hit / ult_butt the kit's CasterAnimations)
    ("league_ornn", 1.5, include_str!("../../../league/champions/league_ornn#anim.fanim")),
    // Shyvana: posed by tools/art/rig_shyvana.py on Codex's step-1 takes at the user's 1.5 squares a game pixel (63 game
    // rows horn tips to soles, the dragon 64 as drawn: 「人42 龙48 PPU1.5」; 3/4 only; her actions on Codex's skeleton poses
    // with the design's head; the dragon's d_* tags the kit's CasterAnimations), so no SIZES row
    ("league_shyvana", 1.5, include_str!("../../../league/champions/league_shyvana#anim.fanim")),
    // Heimerdinger: the design (Codex's step-1 A-2 at the user's 1.5 squares a game pixel, 54 rows hair top to soles:
    // 「36」「PPU 1.5」; 3/4 only) with Codex's whole-body poses and the backpack crane / R's gear props, posed by
    // tools/art/rig_heimerdinger.py after League's clips; attack_w the kit's CasterAnimation (W's third attack), so no
    // SIZES row; brought down to 1.2 (2026-10-22: 「像素太高了 可以调低一点」, tools/art/ppu_restyle.py)
    ("league_heimerdinger", 1.2, include_str!("../../../league/champions/league_heimerdinger#anim.fanim")),
    // Naafiri: posed by tools/art/rig_naafiri.py on Codex's step-1 takes A-2 / P-2 and its key poses at the user's 1.5
    // squares a game pixel (45 game rows blade tip to paws: 「30」「PPU 1.5」; 3/4 only; her pack drawn into her frames, the
    // p4_* tags the four hounds league_naafiri's view hook swaps in during The Call of the Pack), so no SIZES row
    ("league_naafiri", 1.5, include_str!("../../../league/champions/league_naafiri#anim.fanim")),
    // Udyr: his four stances (the plain guard, the bear q_*, the ram e_*, the phoenix r_*) posed by tools/art/rig_udyr.py on
    // Codex's step-1 takes and its key poses at the user's 1.5 squares a game pixel (60 game rows fists to soles: 「40」
    // 「PPU 1.5」; 3/4 only; league_udyr's view hook swaps in the stance's idle / run / hit / dead), so no SIZES row
    ("league_udyr", 1.5, include_str!("../../../league/champions/league_udyr#anim.fanim")),
    // Qiyana: posed by tools/art/rig_qiyana.py on Codex's step-1 take A-1 and its key poses (the legs drawn again at the
    // design's chibi length) at the user's 1.5 squares a game pixel (60 game rows crest to soles: 「40」「PPU 1.5」; 3/4
    // only; Q's sweep in four looks, skill / skill_w / skill_r / skill_g, by the element on her ring), so no SIZES row
    ("league_qiyana", 1.5, include_str!("../../../league/champions/league_qiyana#anim.fanim")),
    // Hwei: posed by tools/art/rig_hwei.py on Codex's step-1 take A-1 and its key poses (the design's head and brush put
    // back, the legs drawn again at the design's chibi length) at the user's 1.5 squares a game pixel (60 game rows hair
    // to soles, the crescent of paint above: 「头发顶到脚底 40 游戏像素，PPU 1.5」; 3/4 only; Disaster's three and Torment's
    // three each their own tag), so no SIZES row
    ("league_hwei", 1.5, include_str!("../../../league/champions/league_hwei#anim.fanim")),
    // Ivern: posed by tools/art/rig_ivern.py on Codex's step-1 take A-2 and its key poses (the design's head put back,
    // the standing poses' legs drawn again at the design's chibi length) at the user's 1.5 squares a game pixel (60 game
    // rows mushroom to soles: 「艾翁蘑菇顶到脚底 40 游戏像素 … PPU 1.5，只做四分之三侧面」), so no SIZES row
    ("league_ivern", 1.5, include_str!("../../../league/champions/league_ivern#anim.fanim")),
    // Illaoi: posed by tools/art/rig_illaoi.py on Codex's step-1 take A-2 and its key poses (the design's head put back,
    // the long-legged poses' and the runs' legs drawn again at the design's length) at the user's 1.5 squares a game pixel
    // (63 game rows bun to soles: 「俄洛伊发髻到脚底 42 游戏像素，PPU 1.5，触手 44，只做四分之三侧面」), so no SIZES row
    ("league_illaoi", 1.5, include_str!("../../../league/champions/league_illaoi#anim.fanim")),
    // Aurora: posed by tools/art/rig_aurora.py on Codex's step-1 take A-2 and its key poses (the design's head put back,
    // the long-legged poses' legs drawn again at the design's length) at the user's 2.25 squares a game pixel (86 game
    // rows hat top to soles, the ears above: 「太模糊了 用PPU调下像素」, then A-2 at 2.25; 3/4 only), so no SIZES row
    ("league_aurora", 2.25, include_str!("../../../league/champions/league_aurora#anim.fanim")),
    // Nunu & Willump: posed by tools/art/rig_nunu.py on Codex's step-1 take A-2 and its key poses (the design's Nunu head
    // put back, Willump's size set pose by pose) at the user's 1.37 squares a game pixel (63 game rows pompom to soles:
    // 「努努用 A-2，PPU 1.37（46 游戏像素）」; 3/4 only), so no SIZES row
    ("league_nunu", 1.37, include_str!("../../../league/champions/league_nunu#anim.fanim")),
    // Azir: posed by tools/art/rig_azir.py on Codex's step-1 take A-2 (the sceptre straightened) and its key poses (the
    // design's helmet put back, each body read at its skeleton's height) at the user's 1.5 squares a game pixel (57 game
    // rows crest to soles, the sceptre above: 「38」「PPU 1.5」; 3/4 only), so no SIZES row
    ("league_azir", 1.5, include_str!("../../../league/champions/league_azir#anim.fanim")),
    // Zac: posed by tools/art/rig_zac.py on Codex's step-1 take A-1 and its key poses after League's clips (the design's
    // head and tendril put back on the eyes; the add-on's puddle in the split_* tags) at the user's 1.5 squares a game
    // pixel (66 game rows tendril top to soles = 44 game px; 3/4 only), shown at 85 % (SIZES)
    ("league_zac", 1.5, include_str!("../../../league/champions/league_zac#anim.fanim")),
    // Singed: posed by tools/art/rig_singed.py on Codex's step-1 take A-2 as drawn and its key poses after League's clips
    // (the design's head put back, the bodies brought to the design's size) at the user's 1.39 squares a game pixel (its
    // own squares: 50 game rows head top to soles = 36 game px, the tank above; 3/4 only), so no SIZES row
    ("league_singed", 1.39, include_str!("../../../league/champions/league_singed#anim.fanim")),
    // Bel'Veth: posed by tools/art/rig_belveth.py on Codex's step-1 take A-1 cut to 82 rows and its key poses after
    // League's clips (the design's head put back, the bodies brought to the design's size) at the user's 1.75 squares a
    // game pixel (71 game rows head top to claws = 40 game px, the shoulder spikes above; 3/4 only), so no SIZES row
    ("league_belveth", 1.75, include_str!("../../../league/champions/league_belveth#anim.fanim")),
    // Taliyah: posed by tools/art/rig_taliyah.py on Codex's step-1 take A-2 cut to 70 rows and its key poses after
    // League's clips (read at their bodies' scale, the design's head put back) at the user's 1.75 squares a game pixel
    // (70 rows hair top to soles = 40 game px; the surf and the ride on her boulder higher; 3/4 only), so no SIZES row
    ("league_taliyah", 1.75, include_str!("../../../league/champions/league_taliyah#anim.fanim")),
    // Aurelion Sol: posed by tools/art/rig_aurelionsol.py on Codex's step-1 take A-2 as drawn (77 rows crest to tail tip
    // = 44 game px, hovering 4 rows over the ground; the flight on take B-2) and its key poses after League's clips (the
    // design's head put back, the bodies brought to the design's size) at the user's 1.75 squares a game pixel (3/4
    // only), so no SIZES row
    ("league_aurelionsol", 1.75, include_str!("../../../league/champions/league_aurelionsol#anim.fanim")),
    // Sejuani: posed by tools/art/rig_sejuani.py on Codex's PPU-2.0 redraw of her step-1 take A-2 (72 rows ice horn tip
    // to hooves = 36 game px, riding Bristle) and its key poses after League's clips (her design head put back, Bristle
    // brought to the design's size) at the user's 2.0 squares a game pixel (3/4 only), so no SIZES row
    ("league_sejuani", 2.0, include_str!("../../../league/champions/league_sejuani#anim.fanim")),
    // Kled: posed by tools/art/rig_kled.py on Codex's step-1 take A-1 (80 rows hat spike to Skaarl's claws = 40 game px)
    // and, on foot, B-1 under A-1's head, with their key poses after League's clips (the design's head put back, Skaarl and
    // the on-foot bodies brought to the designs' size) at the user's 2.0 squares a game pixel (3/4 only), so no SIZES row
    ("league_kled", 2.0, include_str!("../../../league/champions/league_kled#anim.fanim")),
    // Yorick: posed by tools/art/rig_yorick.py on Codex's step-0 take A-2 as drawn (83 rows shovel tip to boots = 48 game
    // px) and its key poses after League's clips (the design's head put back) at the user's 1.75 squares a game pixel (3/4
    // only), so no SIZES row
    ("league_yorick", 1.75, include_str!("../../../league/champions/league_yorick#anim.fanim")),
    // Ambessa: posed by tools/art/rig_ambessa.py on Codex's step-1 take A-1 with its head cut to 27 % (96 rows hair to
    // soles = 48 game px, the blades out to her sides) and its key poses after League's clips (read at each body's own
    // scale, the design's head put back) at the user's 2.0 squares a game pixel (3/4 only), shown at 85 % (SIZES)
    ("league_ambessa", 2.0, include_str!("../../../league/champions/league_ambessa#anim.fanim")),
    // Rumble: posed by tools/art/rig_rumble.py on Codex's step-1 take B-1 as drawn (62 rows mohawk to the red feet = 36
    // game px) and its key poses after League's clips (the design's head put back) at the user's 1.75 squares a game
    // pixel (3/4 only; Overheat's red-hot oh_* tags and Flamespitter-on-the-move's q_run / q_stand league_rumble's view
    // hook swaps in), so no SIZES row
    ("league_rumble", 1.75, include_str!("../../../league/champions/league_rumble#anim.fanim")),
    // Trundle: posed by tools/art/rig_trundle.py on Codex's step-0 take A-1 as drawn (85 rows mane to feet = 42.5 game
    // px, hunched, the ice club out to 52 px) and its key poses after League's clips (the design's head put back) at the
    // user's 2.0 squares a game pixel (3/4 only), so no SIZES row
    ("league_trundle", 2.0, include_str!("../../../league/champions/league_trundle#anim.fanim")),
    // Skarner: posed by tools/art/rig_skarner.py on Codex's step-0 picture A as drawn (59 rows stinger tips to feet = 33.7
    // game px, 80 squares = 46 px wide) and Codex's key poses after League's clips (read back at the body's size, the
    // design's head put back) at the user's 1.75 squares a game pixel (3/4 only), so no SIZES row
    ("league_skarner", 1.75, include_str!("../../../league/champions/league_skarner#anim.fanim")),
    // Zaahen: posed by tools/art/rig_zaahen.py on Codex's step-0 take A-2 brought to 84 rows (48 game px horn tips to
    // soles, the glaive and the wings out to 50) and Codex's key poses after League's clips (read back at the design's
    // size, the design's head put back) at the user's 1.75 squares a game pixel (3/4 only), so no SIZES row
    ("league_zaahen", 1.75, include_str!("../../../league/champions/league_zaahen#anim.fanim")),
    // Neeko: posed by tools/art/rig_neeko.py on Codex's step-1 take A-1 and its key poses at the user's 2.5 squares a
    // game pixel (100 game rows quill tips to soles: 「40」, then 「1.5也挺糊的 还得往上调整吧」; 3/4 only; league_neeko's
    // view hook draws her as an ally while she is disguised), so no SIZES row
    ("league_neeko", 2.5, include_str!("../../../league/champions/league_neeko#anim.fanim")),
    // Xerath: re-adjusted at 1.55 squares a game pixel (tools/art/design_xerath_hd.py: Codex's draft B on its own grid,
    // slimmer with a smaller head, then shortened - 「泽拉斯在游戏里身体太长了吧？」 - 62 rows crown to spike tips = 40 game
    // px: 「不是重做 是重新调整」「游戏里别太大就行」), every action posed after League's clips by tools/art/rig_xerath_hd.py
    // (R: his armour in a ring round the core), so no SIZES row
    ("league_xerath", 1.55, include_str!("../../../league/champions/league_xerath#anim.fanim")),
    // K'Sante: posed by tools/art/rig_ksante.py on Codex's step-1 takes A-2 / O-1 at the user's 1.5 squares a game pixel
    // (72 game rows ntofo tops to soles: 「陀斧顶到脚底 48 游戏像素，PPU 1.5」; 3/4 only; Codex's 27 skeleton poses with the
    // design's head; the ao_* tags All Out's, the kit's CasterAnimations and league_ksante's view hook), so no SIZES row;
    // brought down to 1.2 (2026-10-22: 「奎桑提像素也太高了」, tools/art/ppu_restyle.py)
    ("league_ksante", 1.2, include_str!("../../../league/champions/league_ksante#anim.fanim")),
    // 2026-10-16 redo from Codex's pictures, the actions posed from the designs (tools/art/rig_<hero>_hd.py; Nami's after
    // League's own clips, tools/lol/league_joints.py), PPU 1.5 at their old heights, so no SIZES rows
    ("league_morgana", 1.5, include_str!("../../../league/champions/league_morgana#anim.fanim")),
    ("league_nami", 1.5, include_str!("../../../league/champions/league_nami#anim.fanim")),
    ("league_janna", 1.5, include_str!("../../../league/champions/league_janna#anim.fanim")),
    // Jax: Codex's redrawn chibi design facing front-right (assets/source/jax/PICTURE_PROMPT.md), posed after League's own
    // clips by tools/art/rig_jax_hd.py (his run league_braum's walk), PPU 1.5 at his old 36 rows, so no SIZES row
    ("league_jax", 1.5, include_str!("../../../league/champions/league_jax#anim.fanim")),
    // Xin Zhao (2026-10-18): Codex's chibi picture (assets/source/xinzhao/PICTURE_PROMPT_PPU.md) cut to 63 rows, posed
    // after League's own clips by tools/art/rig_xinzhao_hd.py, PPU 1.5 at his old 42 rows, so no SIZES row
    ("league_xinzhao", 1.5, include_str!("../../../league/champions/league_xinzhao#anim.fanim")),
    // Kai'Sa (2026-10-18): Codex's chibi picture (assets/source/kaisa/PICTURE_PROMPT_PPU.md) read back on its own grid,
    // posed after League's own clips by tools/art/rig_kaisa_hd.py (the run's legs Codex's redraw), PPU 1.45 at her old 42
    // rows, so no SIZES row
    ("league_kaisa", 1.45, include_str!("../../../league/champions/league_kaisa#anim.fanim")),
    // Camille (2026-10-18): Codex's design picture (assets/source/camille/PICTURE_PROMPT_PPU.md) read back on its own
    // grid and cut to 69 rows, the upper body posed after League's own clips by tools/art/rig_camille_hd.py, the legs of
    // her kicks and leaps Codex's drawing along League's guides, PPU 1.5 at her old 46 rows, so no SIZES row
    ("league_camille", 1.5, include_str!("../../../league/champions/league_camille#anim.fanim")),
    // Fiora (2026-10-18): Codex's design picture (assets/source/fiora/PICTURE_PROMPT_PPU.md) read back on one fitted
    // grid and cut to 60 rows with her whole head kept, posed after League's own clips by tools/art/rig_fiora_hd.py (the
    // blade drawn straight, the legs of her steps and lunges drawn on League's bones in the design's colours), PPU 1.5
    // at her old 40 rows, so no SIZES row
    ("league_fiora", 1.5, include_str!("../../../league/champions/league_fiora#anim.fanim")),
    // LeBlanc: PPU 2.0 (「PPU 2.0 原样」) - Codex's take A of 2026-10-02 as drawn (51 x 86 squares, the staff straightened),
    // posed after League's clips by tools/art/rig_leblanc_hd.py, the run on Codex's legs
    ("league_leblanc", 2.0, include_str!("../../../league/champions/league_leblanc#anim.fanim")),
    // Darius (2026-10-18): Codex's design picture (assets/source/darius/PICTURE_PROMPT_PPU.md) read back on its own
    // grid, nothing cut (56 x 61), posed after League's own clips by tools/art/rig_darius_hd.py (the axe hand and the axe
    // turned losslessly, the run on his own legs moved whole), PPU 1.45 at his old 42 rows, so no SIZES row
    ("league_darius", 1.45, include_str!("../../../league/champions/league_darius#anim.fanim")),
    // Riven (2026-10-18): Codex's design picture (assets/source/riven/PICTURE_PROMPT_PPU.md) read back on its own grid
    // (68 x 61), her sword one of Codex's angle drawings in her fist (tools/art/swords_riven_hd.py); idle, run, ult, hit
    // and death posed after League's clips by tools/art/rig_riven_hd.py, her three attacks (taking turns), Broken Wings
    // and Valor Codex's whole-frame redraws (tools/art/actions_riven_hd.py); PPU 1.5 at her old 40 rows, so no SIZES row
    ("league_riven", 1.5, include_str!("../../../league/champions/league_riven#anim.fanim")),
    // Caitlyn (2026-10-23): Codex's design picture (assets/source/caitlyn/PICTURE_PROMPT_PPU.md) read back on its own
    // grid (54 x 65), her actions Codex's whole-frame redraws (pack_caitlyn_actions.py) with the rifle drawn straight
    // square by square (rifle_caitlyn.py), stood by tools/art/rig_caitlyn_hd.py; PPU 1.45 at her old 45 rows
    ("league_caitlyn", 1.45, include_str!("../../../league/champions/league_caitlyn#anim.fanim")),
    // Varus (2026-10-23): Codex's design picture (assets/source/varus/PICTURE_PROMPT_PPU.md) read back on its own grid
    // (58 x 59), every action posed from the design's own squares by tools/art/rig_varus_hd.py (the bow lifted, the near
    // arm turned level, run and kneel legs drawn from the design's leg rows); PPU 1.35: his body the old 39 rows (1.5
    // drew it 35: 「维鲁斯建模小了」)
    ("league_varus", 1.35, include_str!("../../../league/champions/league_varus#anim.fanim")),
    // Jinx (2026-10-23): the user's own side-view picture read back on its 22.23-px grid (88 x 82,
    // tools/art/design_jinx_hd.py) with Fishbones drawn in behind her braids, every action posed from the design's own
    // squares by tools/art/rig_jinx_hd.py (arms never moved, the run's thighs the design's stocking rows along the bone
    // with its whole boots); PPU 2.2 at her old 37 rows, so no SIZES row
    ("league_jinx", 2.2, include_str!("../../../league/champions/league_jinx#anim.fanim")),
    // Lux (2026-10-23): Codex's picture read back at PPU 2.2 (64 x 81, tools/art/design_lux_hd.py, the staff drawn
    // straight); idle, run, hit and death posed from the design's own squares (tools/art/rig_lux_hd.py), the four casts
    // Codex's whole-frame redraw mended onto the design (tools/art/casts_lux_hd.py); 37 rows, so no SIZES row
    ("league_lux", 2.2, include_str!("../../../league/champions/league_lux#anim.fanim")),
    // Ahri (2026-10-24): Codex's picture read back at PPU 2.2 (78 x 88, tools/art/design_ahri_hd.py, the eyes and face
    // set by hand); every action Codex's whole-frame redraw mended onto the design (tools/art/casts_ahri_hd.py: the
    // design's head, her size, the nine tails joined to her hair); 40 rows, so no SIZES row
    ("league_ahri", 2.2, include_str!("../../../league/champions/league_ahri#anim.fanim")),
    // Twitch (2026-10-24): the user's own picture read back at PPU 2.2 (109 x 71, tools/art/design_twitch_hd.py, the goggle
    // and the grin redrawn by hand); every action Codex's whole-frame redraw mended onto the design
    // (tools/art/casts_twitch_hd.py: the design's head, his size; rig_twitch_hd.py: Venom Cask thrown overhead by the far
    // arm, not a third one); 32 rows as his 1x sprite, so no SIZES row
    ("league_twitch", 2.2, include_str!("../../../league/champions/league_twitch#anim.fanim")),
    // Annie (2026-10-24): Codex's take A read back at PPU 2.2 (44 x 75, tools/art/design_annie_hd.py, the face set by
    // hand); every action Codex's whole-frame redraw mended onto the design (tools/art/casts_annie_hd.py: the design's
    // head, her size, the ground), Tibbers in her near hand; 34 rows as her 1x sprite, so no SIZES row
    ("league_annie", 2.2, include_str!("../../../league/champions/league_annie#anim.fanim")),
    // Gwen (2026-10-25): Codex's v2 picture (the user's own Gemini picture redrawn) read as drawn at PPU 2.84 (93 x 116,
    // tools/art/design_gwen_hd.py); every action Codex's whole-frame redraw mended onto the design
    // (tools/art/casts_gwen_hd.py: the scissors full size and always in her right hand); 38 rows as her 1x sprite, so
    // no SIZES row
    ("league_gwen", 2.84, include_str!("../../../league/champions/league_gwen#anim.fanim")),
    // Samira (2026-10-25): Codex's v3 picture (head 26%) read as drawn at PPU 2.84 (76 x 105,
    // tools/art/design_samira_hd.py, the sword behind her straightened by tools/art/sword_samira_hd.py); every action
    // Codex's whole-frame redraw read onto the design (tools/art/casts_samira_hd.py: the sword always in her far hand);
    // 37 rows as her 1x sprite, so no SIZES row. In game she looked thin at 2.84 (「感觉降低像素就行了」): laid out
    // at 2.2 squares on her 2.84 grid with the face kept as drawn (ppu_restyle.py look, 「脸做好点啊」)
    ("league_samira", 2.84, include_str!("../../../league/champions/league_samira#anim.fanim")),
    // Draven (2026-10-26): the user's own picture (「就用这个就行」) drawn at PPU 2.2 on 11-px squares, read back exactly
    // (114 x 76, tools/art/design_draven_hd.py); every action Codex's whole-frame redraw of his old frame in its old
    // pose read onto the design (tools/art/casts_draven_hd.py); 34.5 rows as his 1x sprite's 35, so no SIZES row
    ("league_draven", 2.2, include_str!("../../../league/champions/league_draven#anim.fanim")),
    // Lee Sin (2026-10-26): Codex's picture traced from his sprite read on its own squares (68 x 86,
    // tools/art/design_leesin_hd.py: 86 rows / 2.1 = his 41); every action Codex's whole-frame redraw of his old frame
    // read onto it at the zoom his head gives (tools/art/casts_leesin_hd.py), the run drawn again on League's legs;
    // brought to 1.5 squares a game pixel (「ppu像素太高了 降低点」「用 1.5」, ppu_restyle.py); drawn at 90 %, then
    // 95 % (SIZES), back to 100 % = no SIZES row (「盲僧在游戏里和其他英雄有点格格不入 感觉太小了」: 38.6 game px
    // against the released heroes' median 41, Garen 41.6, Darius 43.4; the user picked 100 %)
    ("league_leesin", 1.5, include_str!("../../../league/champions/league_leesin#anim.fanim")),
    // Vayne (2026-10-26): the user's own picture (「就用这个啊」) read on its own squares (85 x 102,
    // tools/art/design_vayne_hd.py: 102 rows / 2.55 = her 40); every action Codex's whole-frame redraw of her old frame
    // read onto it at the zoom her head gives (tools/art/casts_vayne_hd.py: the run on one head column, its second half
    // the first); brought to 2.2 squares a game pixel (「通过，用 2.2」, ppu_restyle.py); 40 game px as her 1x sprite, so
    // no SIZES row
    ("league_vayne", 2.2, include_str!("../../../league/champions/league_vayne#anim.fanim")),
    // Lucian (2026-10-26, 「模型要和英雄联盟像一点」): Codex's picture after League's Lucian in his old sprite's pose,
    // read on its raw's own squares (111 x 93, tools/art/design_lucian_hd.py: 93 rows / 46 = 2.02, 「通过，用 2.02
    // 原样」); every action Codex's whole-frame redraw of his old frame read onto it at the zoom his head gives
    // (tools/art/casts_lucian_hd.py: the run on one head column, its second half the first); 46 game px as his 1x
    // sprite, so no SIZES row
    // brought to 1.5 squares a game pixel (「卢锡安的像素太高了调低一点 新模型」「卢锡安用 1.5」, ppu_restyle.py)
    ("league_lucian", 1.5, include_str!("../../../league/champions/league_lucian#anim.fanim")),
    // Locke (2026's new champion, the user's pick): posed by tools/art/rig_locke.py on Codex's step-0 take A-1 brought to
    // 88 rows (44 game px hair to soles) and its key poses after League's clips (the design's head put back, the bodies
    // Codex drew bigger read at the design's size) at the user's 2.0 squares a game pixel (3/4 only; his W look's w_*
    // tags league_locke's view hook swaps in), so no SIZES row
    ("league_locke", 2.0, include_str!("../../../league/champions/league_locke#anim.fanim")),
    // Yunara: PPU 1.5 (the user's pick), posed from the design's own squares at that density by tools/art/rig_yunara.py
    // (40 game rows ornaments to soles), so no SIZES row
    ("league_yunara", 1.5, include_str!("../../../league/champions/league_yunara#anim.fanim")),
    // Rengar (2026-10-27, 「利用PPU1.5重做一下狮子狗模型」): Codex's picture traced from his old sprite read on its raw's own
    // squares (74 x 59, tools/art/design_rengar_hd.py: 59 rows / 40 = 1.475), his tail behind him (drawn, the picture had
    // it in front); every action Codex's whole-frame redraw of his old frame read onto it at the zoom his head gives
    // (tools/art/casts_rengar_hd.py), the run his old trot rebuilt from the design (tools/art/rig_rengar_hd.py); 40 game
    // px as his 1x sprite, so no SIZES row
    ("league_rengar", 1.475, include_str!("../../../league/champions/league_rengar#anim.fanim")),
    // Syndra (2026-10-27, 「接下来可以重做辛德拉」, 「就用原样 1.86」): Codex's picture traced from her old sprite read on its
    // raw's own squares (54 x 78, tools/art/design_syndra_hd.py: 78 rows / 42 = 1.857); her old sheet was her idle frame
    // moved whole with the far hand or the legs redrawn, so every frame is the design moved as the old one moved, the far
    // arm from Codex's pose pictures (tools/art/casts_syndra_hd.py, rig_syndra_hd.py); 42 game px as her 1x sprite, so
    // no SIZES row
    ("league_syndra", 1.857, include_str!("../../../league/champions/league_syndra#anim.fanim")),
    // Akali (2026-10-27, 「下一个英雄重做阿卡丽」, 「设计图通过，就用 1.8」): Codex's fourth take read as drawn on its own
    // 16-px squares (71 x 72, tools/art/design_akali_hd.py: 72 rows / 40 = 1.8; the hook in the near hand, the blade in
    // the far one - 「不用照旧精灵的手」); every action Codex's whole-frame redraw of her old frame read onto it at the zoom
    // her head gives (tools/art/casts_akali_hd.py, rig_akali_hd.py; the dashes baked as before); 40 game px as her 1x
    // sprite, so no SIZES row
    ("league_akali", 1.8, include_str!("../../../league/champions/league_akali#anim.fanim")),
    // Sivir (2026-10-28, 「下一个英雄重做希维尔吧」, 「通过，用 2.25」): Codex's picture read as drawn on its own 11.6-px
    // squares (98 x 81, tools/art/design_sivir_hd.py: 81 rows / 36 = 2.25); every action Codex's whole-frame redraw of her
    // old frame read onto it at the zoom her head gives (tools/art/casts_sivir_hd.py, rig_sivir_hd.py; the Q throw and
    // the W / catch pictures baked as before); 36 game px as her 1x sprite, so no SIZES row
    ("league_sivir", 2.25, include_str!("../../../league/champions/league_sivir#anim.fanim")),
    // Tristana (2026-10-28, 「下一个英雄重做崔丝塔娜」, 「通过，用 2.56」): Codex's raw read as drawn on its own drifting
    // squares (103 x 87, tools/art/design_tristana_hd.py: 87 rows / 34 = 2.56); every action Codex's whole-frame redraw of
    // her old frame read onto it at the zoom her head gives (tools/art/casts_tristana_hd.py, rig_tristana_hd.py; the
    // muzzle pictures baked as before); 34 game px as her 1x sprite, so no SIZES row
    ("league_tristana", 2.559, include_str!("../../../league/champions/league_tristana#anim.fanim")),
    // Zed (2026-10-28, 「下一个英雄重做劫」, 「通过，用 1.62」): Codex's zed-A read as drawn (40 x 65,
    // tools/art/design_zed_hd.py: 65 rows / 40 = 1.625); every action Codex's whole-frame redraw of his old frame read
    // onto it at the zoom his figure and head give (tools/art/casts_zed_hd.py, rig_zed_hd.py; nothing baked - his
    // shadows, shurikens and slashes are effect strips); 40 game px as his 1x sprite, so no SIZES row
    ("league_zed", 1.625, include_str!("../../../league/champions/league_zed#anim.fanim")),
    // Taric (2026-10-29, 「下一个英雄重做塔里克」, 「通过，用 1.55」): Codex's taric-A read as drawn (48 x 62,
    // tools/art/design_taric_hd.py: 62 rows / 40 = 1.55); every action Codex's pixel rig of it - the design cut into
    // parts, turned whole - rigged again and posed on his old frames (tools/art/casts_taric_hd.py, rig_taric_hd.py;
    // nothing baked - his starlight, beams and shields are effect strips); 40 game px as his 1x sprite, so no SIZES row
    ("league_taric", 1.55, include_str!("../../../league/champions/league_taric#anim.fanim")),
    // Kayle (2026-10-29, 「下一个英雄重做天使」, 「通过，用 2.29」): Codex's kayle-A read as drawn (66 x 112,
    // tools/art/design_kayle_hd.py: 112 rows / 49 = 2.286, wing tips to sword tip); every action Codex's whole-frame
    // redraw of her old frame read onto it at the zoom her figure and head give (tools/art/casts_kayle_hd.py,
    // rig_kayle_hd.py; nothing baked - her fire, waves and blades are effect strips); 49 game px as her 1x sprite and
    // hovering 2 px as before, so no SIZES row
    ("league_kayle", 2.286, include_str!("../../../league/champions/league_kayle#anim.fanim")),
    // Leona (2026-10-30, 「接下来重做曙光女神」, 「通过，用 1.76」): Codex's leona-A read as drawn (69 x 72,
    // tools/art/design_leona_hd.py: 72 rows / 41 = 1.756); every action Codex's whole-frame redraw of her old frame
    // read onto it at the zoom her figure and head give (tools/art/casts_leona_hd.py, rig_leona_hd.py; nothing baked -
    // her sunlight, eclipse and flare are effect strips); 41 game px as her 1x sprite, so no SIZES row. Then
    // 「另外蕾欧娜的模型太高清了 降低点像素」: drawn at 1.756, brought to 1.5 (tools/art/review_leona_ppu.py, 「蒾欧娜用 1.5」)
    ("league_leona", 1.5, include_str!("../../../league/champions/league_leona#anim.fanim")),
    // Sona (2026-10-30, 「接下来重做琴女」, 「调高PPU像素」「达到和我给你的图一样的效果」, 「通过，用 3.88」): the user's
    // picture read on its finest squares (117 x 155, tools/art/design_sona_hd.py: 155 rows / 40 = 3.875); every action
    // Codex's whole-frame redraw of her old frame read onto it at the zoom her figure, head and height give
    // (tools/art/casts_sona_hd.py, rig_sona_hd.py; nothing baked); 40 game px as her 1x sprite, so no SIZES row
    ("league_sona", 3.875, include_str!("../../../league/champions/league_sona#anim.fanim")),
    // Briar (2026-10-30, 「下一个英雄重做贝蕾亚」, 「算了用2.94吧」): Codex's briar-A read on ~8.5-px squares (110 x 135,
    // tools/art/design_briar_hd.py: 135 rows / 46 = 2.935); every action Codex's whole-frame redraw of her old frame read
    // onto it at the zoom her figure, pink hair and pillory give (tools/art/casts_briar_hd.py, rig_briar_hd.py; nothing
    // baked but the Snack's blood drops); 46 game px as her 1x sprite, so no SIZES row
    ("league_briar", 2.935, include_str!("../../../league/champions/league_briar#anim.fanim")),
    // Talon (2026-10-31, 「下一个英雄重做泰隆」, 「用A PPU2.21吧」): Codex's talon-A read on its own ~10.5-px squares
    // (105 x 86, tools/art/design_talon_hd.py: 86 rows / 39 = 2.205); every action Codex's whole-frame redraw of his old
    // frame read onto it at the zoom his figure and face give (tools/art/casts_talon_hd.py, rig_talon_hd.py; the run
    // redrawn with the legs changing over, 「走路没有换腿」; nothing baked); 39 game px as his 1x sprite. Then 「男刀局内体型有点
    // 过大了 缩小一点」「太高清 加点黑色描边吧」(2026-10-31): brought to 1.5 with an outline (RESTYLE talon), 90 % in game (SIZES)
    ("league_talon", 1.5, include_str!("../../../league/champions/league_talon#anim.fanim")),
    // Thresh (2026-10-31, 「锤石和女枪在这个pr里一起重做二轮」, 「都用中间档」): Codex's thresh-A read on its own ~9.75-px
    // squares (90 x 99, tools/art/design_thresh_hd.py: 99 rows / 40 = 2.475); every action Codex's whole-frame redraw of
    // his old frame read onto it at the zoom its height (or its area) gives (tools/art/casts_thresh_hd.py,
    // rig_thresh_hd.py; nothing baked); 40 game px as his 1x sprite, so no SIZES row
    ("league_thresh", 2.475, include_str!("../../../league/champions/league_thresh#anim.fanim")),
    // Miss Fortune (2026-10-31, the same PR, 「都用中间档」): Codex's missfortune-A read on its own ~9.75-px squares (80 x
    // 105, tools/art/design_missfortune_hd.py: 105 rows / 38 = 2.763); every action Codex's whole-frame redraw of her old
    // frame read onto it at the zoom its height (the deaths: its area; E 2-6 by the hat) gives
    // (tools/art/casts_missfortune_hd.py, rig_missfortune_hd.py; nothing baked); 38 game px as her 1x sprite, so no SIZES row
    ("league_missfortune", 2.763, include_str!("../../../league/champions/league_missfortune#anim.fanim")),
    // Senna (2026-11-01, 「下一个英雄我们重做赛娜」, 「用 A 1.87」): Codex's senna-A read on its own ~14.4-px
    // squares (82 x 73, tools/art/design_senna_hd.py: 73 rows / 39 = 1.872); every action Codex's whole-frame redraw of her
    // old frame read onto it at the zoom her height and face give (tools/art/casts_senna_hd.py, rig_senna_hd.py; the run
    // and Q's first two frames redrawn: the legs changing over, the cannon low; nothing baked); 39 game px as her 1x
    // sprite, so no SIZES row
    ("league_senna", 1.872, include_str!("../../../league/champions/league_senna#anim.fanim")),
    // Evelynn (2026-11-01, 「伊芙琳和瑟提也在这个pr里重做」, 「伊芙琳用2.78」): Codex's evelynn-A read on its own
    // ~10.4-px squares (103 x 114, tools/art/design_evelynn_hd.py: 114 rows / 41 = 2.780); every action Codex's
    // whole-frame redraw of her old frame read onto it at the zoom her height and hair give (tools/art/casts_evelynn_hd.py,
    // rig_evelynn_hd.py; nothing baked); 41 game px as her 1x sprite, so no SIZES row
    ("league_evelynn", 2.780, include_str!("../../../league/champions/league_evelynn#anim.fanim")),
    // Sett (2026-11-01, 「伊芙琳和瑟提也在这个pr里重做」, 「瑟提用1.79」): Codex's sett-A read on its own ~15.5-px
    // squares (53 x 75, tools/art/design_sett_hd.py: 75 rows / 42 = 1.786); every action Codex's whole-frame redraw of
    // his old frame read onto it at the zoom between his height and his hair (tools/art/casts_sett_hd.py, rig_sett_hd.py;
    // nothing baked); 42 game px as his 1x sprite, so no SIZES row
    ("league_sett", 1.786, include_str!("../../../league/champions/league_sett#anim.fanim")),
    // Viego (2026-11-01, 「再加一个佛耶戈重做吧」, 「佛耶戈用2.45」): Codex's viego-A read on its own ~9.8-px
    // squares (114 x 115, tools/art/design_viego_hd.py: 115 rows / 47 = 2.447); every action Codex's whole-frame redraw of
    // his old frame read onto it at the zoom between his height and his hair (tools/art/casts_viego_hd.py, rig_viego_hd.py;
    // nothing baked); 47 game px as his 1x sprite, so no SIZES row
    ("league_viego", 2.447, include_str!("../../../league/champions/league_viego#anim.fanim")),
    // Diana (2026-11-02, 「接下来可以重做 戴安娜 易大师 瑞兹」, 「戴安娜1.81 剑圣2.23 瑞兹1.66」): Codex's diana-A read on its own ~15.7-px
    // squares (49 x 78, tools/art/design_diana_hd.py: 78 rows / 43 = 1.814); every action Codex's whole-frame redraw of
    // her old frame read onto it at the median of the zooms her height, head and area give
    // (tools/art/casts_diana_hd.py, rig_diana_hd.py; the ult's moon ring and the third strike's slash left out; nothing
    // baked); 43 game px as her 1x sprite, so no SIZES row
    ("league_diana", 1.814, include_str!("../../../league/champions/league_diana#anim.fanim")),
    // Master Yi (the same release): Codex's masteryi-A read on its own ~9.8-px squares (94 x 125,
    // tools/art/design_masteryi_hd.py: 125 rows / 56 = 2.232); every action Codex's whole-frame redraw of his old frame
    // read onto it at the median of the zooms his height, head and area (ten frames set by eye against the helmet) give
    // (tools/art/casts_masteryi_hd.py, rig_masteryi_hd.py; the outline 3 squares; nothing baked); 56 game px as his 1x
    // sprite, so no SIZES row
    ("league_masteryi", 2.232, include_str!("../../../league/champions/league_masteryi#anim.fanim")),
    // Ryze (the same release): Codex's ryze-A read on its own ~14.7-px squares (42 x 68, tools/art/design_ryze_hd.py:
    // 68 rows / 41 = 1.659); every action Codex's whole-frame redraw of his old frame read onto it at the median of the
    // zooms his height, head and area give (tools/art/casts_ryze_hd.py, rig_ryze_hd.py; the hand sparkles left out;
    // nothing baked); 41 game px as his 1x sprite, so no SIZES row
    ("league_ryze", 1.659, include_str!("../../../league/champions/league_ryze#anim.fanim")),
    // Vi (2026-11-03, 「下面重做蔚 崔斯特 艾克」「再加一个吧 萨科」, 「蔚1.82 卡牌2.7 艾克1.94 萨科2.12」): Codex's vi-A read on its
    // own ~16-px squares (52 x 73, tools/art/design_vi_hd.py: 73 rows / 40 = 1.825); every action Codex's whole-frame
    // redraw of her old frame read onto it at the median of the zooms her height, hair and area give
    // (tools/art/casts_vi_hd.py, rig_vi_hd.py; the Q dash drawn from its native body cells, its dust and the skill_fx1 /
    // ult_fx1 copies baked on again by vi_bake.json); 40 game px as her 1x sprite, so no SIZES row
    ("league_vi", 1.825, include_str!("../../../league/champions/league_vi#anim.fanim")),
    // Twisted Fate (the same release): Codex's twistedfate-A read on ~10.8-px squares (65 x 110,
    // tools/art/design_twistedfate_hd.py: 110 rows / 41 = 2.683, the nearest read to 2.7); every action Codex's whole-
    // frame redraw of his old frame read onto it at the median of the zooms his height, face and area give
    // (tools/art/casts_twistedfate_hd.py, rig_twistedfate_hd.py; Q drawn from its native body cells, its card fan and the
    // attack_fx1 copy baked on again by twistedfate_bake.json); 41 game px as his 1x sprite, so no SIZES row
    ("league_twistedfate", 2.683, include_str!("../../../league/champions/league_twistedfate#anim.fanim")),
    // Ekko (the same release): Codex's ekko-A read on its own ~17-px squares (67 x 68, tools/art/design_ekko_hd.py: 68 rows
    // / 35 = 1.943); every action Codex's whole-frame redraw of his old frame read onto it at the median of the zooms his
    // height, hair crest and area give (tools/art/casts_ekko_hd.py, rig_ekko_hd.py; nothing baked); 35 game px as his 1x
    // sprite, so no SIZES row
    ("league_ekko", 1.943, include_str!("../../../league/champions/league_ekko#anim.fanim")),
    // Shaco (the same release): Codex's shaco-A read on its own ~13-px squares (75 x 91, tools/art/design_shaco_hd.py: 91
    // rows / 43 = 2.116); every action Codex's whole-frame redraw of his old frame read onto it at the median of the zooms
    // his height, hat and area give (tools/art/casts_shaco_hd.py, rig_shaco_hd.py; nothing baked); 43 game px as his 1x
    // sprite, so no SIZES row
    ("league_shaco", 2.116, include_str!("../../../league/champions/league_shaco#anim.fanim")),
    // Nocturne (2026-11-03, 「继续加四个 魔腾 凯南 剑魔 丽桑卓」, 「凯南1.81 梦魇1.8 剑魔2.27 丽桑卓1.81」): Codex's nocturne-A
    // read on its own ~16-px squares (64 x 72, tools/art/design_nocturne_hd.py: 72 rows / 40 = 1.80); every action
    // Codex's whole-frame redraw of his old frame read onto it at the median of the zooms his height, pauldrons and area
    // give (tools/art/casts_nocturne_hd.py, rig_nocturne_hd.py; his white eyes kept where the dark walls them in, the
    // attack_fx1 / ult_fx1 copies baked on again by nocturne_bake.json); 40 game px as his 1x sprite, so no SIZES row
    ("league_nocturne", 1.80, include_str!("../../../league/champions/league_nocturne#anim.fanim")),
    // Kennen (the same release): Codex's kennen-A read on its own ~17.2-px squares (62 x 65, tools/art/design_kennen_hd.py:
    // 65 rows / 36 = 1.806); every action Codex's whole-frame redraw of his old frame read onto it at the median of the
    // zooms his height, face and area give (tools/art/casts_kennen_hd.py, rig_kennen_hd.py; Q drawn from its native body
    // cells, its cast and the attack_fx1 / attack_fx2 / skill2_fx1 copies baked on again by kennen_bake.json); 36 game px
    // as his 1x sprite, so no SIZES row
    ("league_kennen", 1.806, include_str!("../../../league/champions/league_kennen#anim.fanim")),
    // Aatrox (the same release): Codex's aatrox-A read on ~12-px squares (97 x 91, tools/art/design_aatrox_hd.py: 91 rows
    // / 40 = 2.275; his glowing eyes and mouth kept in their own red, the user: 「剑魔的头看起来只看后面」); every action
    // Codex's whole-frame redraw of his old frame read onto it at the median of the zooms his height, chest core and area
    // give (tools/art/casts_aatrox_hd.py, rig_aatrox_hd.py; eight tags drawn from their native body cells, their slashes,
    // fire and chains and the *_fx copies baked on again by aatrox_bake.json); 40 game px as his 1x sprite, so no SIZES row
    ("league_aatrox", 2.275, include_str!("../../../league/champions/league_aatrox#anim.fanim")),
    // Lissandra (the same release): Codex's lissandra-A read on its own ~15-px squares (47 x 76,
    // tools/art/design_lissandra_hd.py: 76 rows / 42 = 1.810); every action Codex's whole-frame redraw of her old frame
    // read onto it at the zoom her crown's width gives (the user: 「丽桑卓有模型一大一小的问题」 - her old glide and death sink,
    // so their heights shrank those frames; death 3-6 by her height, her hands reach the crown) (tools/art/casts_lissandra_hd.py,
    // rig_lissandra_hd.py; Q drawn from its native body cells, its cast and the ult_fx1 / skill2_e_fx1 / skill2_e_fx2
    // copies baked on again by lissandra_bake.json); 42 game px as her 1x sprite, so no SIZES row
    ("league_lissandra", 1.810, include_str!("../../../league/champions/league_lissandra#anim.fanim")),
    // Alistar (2026-11-04, 「接下来重做牛头 蛮王 派克 布兰德」, 「全部粗」): Codex's alistar-A read on its own ~15-px squares
    // (71 x 76, tools/art/design_alistar_hd.py: 76 rows / 44 = 1.727); every action Codex's whole-frame redraw of his old
    // frame read onto it at the median of the zooms his height, horns and area give (tools/art/casts_alistar_hd.py,
    // rig_alistar_hd.py; E's ready glow baked on again into the skill_fx1 / ult_fx1 copies by alistar_bake.json); 44
    // game px as his 1x sprite, so no SIZES row
    ("league_alistar", 1.727, include_str!("../../../league/champions/league_alistar#anim.fanim")),
    // Tryndamere (the same release): Codex's tryndamere-A read on its own ~13.8-px squares (89 x 67,
    // tools/art/design_tryndamere_hd.py: 67 rows / 37 = 1.811); every action Codex's whole-frame redraw of his old frame
    // read onto it at the median of the zooms his height, chest and area give (tools/art/casts_tryndamere_hd.py,
    // rig_tryndamere_hd.py; his death's thrown sword moved to where the old frames have it; R drawn from its native body
    // cells, its fire and the skill_fx1 / skill_q_fx1 copies' spin and heal baked on again by tryndamere_bake.json); 37
    // game px as his 1x sprite, so no SIZES row
    ("league_tryndamere", 1.811, include_str!("../../../league/champions/league_tryndamere#anim.fanim")),
    // Pyke (the same release): Codex's pyke-A read on its own ~16-px squares (68 x 73, tools/art/design_pyke_hd.py: 73
    // rows / 41 = 1.780); every action Codex's whole-frame redraw of his old frame read onto it at the median of the
    // zooms his height, mask and area give (tools/art/casts_pyke_hd.py, rig_pyke_hd.py; Q drawn from its native body
    // cells, its charge glow baked on again by pyke_bake.json; he stands as Codex drew his old idle pose, the design's
    // head being 1.31 times smaller than in every action); 41 game px as his 1x sprite, so no SIZES row
    ("league_pyke", 1.780, include_str!("../../../league/champions/league_pyke#anim.fanim")),
    // Brand (the same release): Codex's brand-A read on its own ~15-px squares (59 x 77, tools/art/design_brand_hd.py: 77
    // rows / 43 = 1.791); every action Codex's whole-frame redraw of his old frame read onto it at the median of the
    // zooms his height, trousers and area give (tools/art/casts_brand_hd.py, rig_brand_hd.py; the attack, W and E into Q
    // drawn from their native body cells, the flashes on his hands baked on again by brand_bake.json); 43 game px as his
    // 1x sprite, so no SIZES row
    ("league_brand", 1.791, include_str!("../../../league/champions/league_brand#anim.fanim")),
    // Kha'Zix (2026-11-05, 「接下来重做螳螂 机器人 莉莉娅 烬」, 「卡兹克2.24 布里茨1.8 莉莉娅2.62 烬1.8」): Codex's khazix-A read
    // on its own ~13.8-px squares (81 x 83, tools/art/design_khazix_hd.py: 83 rows / 37 = 2.243; his thin antennae laid
    // along their skeletons); every action Codex's whole-frame redraw of his old frame read onto it at the zoom its fit
    // over the old frame gives (tools/art/casts_khazix_hd.py, rig_khazix_hd.py; nothing baked); 37 game px as his 1x
    // sprite, so no SIZES row
    ("league_khazix", 2.243, include_str!("../../../league/champions/league_khazix#anim.fanim")),
    // Blitzcrank (the same release): Codex's blitzcrank-A read on its own ~14.4-px squares (80 x 79,
    // tools/art/design_blitzcrank_hd.py: 79 rows / 44 = 1.795); every action Codex's whole-frame redraw of his old frame
    // read onto it at the zoom its fit over the old frame gives (tools/art/casts_blitzcrank_hd.py, rig_blitzcrank_hd.py;
    // the run drawn again with its legs named frame by frame, Q's flying hand an empty socket; nothing baked); 44 game px
    // as his 1x sprite, so no SIZES row
    ("league_blitzcrank", 1.795, include_str!("../../../league/champions/league_blitzcrank#anim.fanim")),
    // Lillia (the same release): Codex's lillia-A read on its own ~8.5-px squares (96 x 139,
    // tools/art/design_lillia_hd.py: 139 rows / 53 = 2.623); every action Codex's whole-frame redraw of her old frame read
    // onto it at the zoom its fit over the old frame gives (tools/art/casts_lillia_hd.py, rig_lillia_hd.py; four legs in
    // the run; nothing baked); 53 game px as her 1x sprite, so no SIZES row
    ("league_lillia", 2.623, include_str!("../../../league/champions/league_lillia#anim.fanim")),
    // Jhin (the same release): Codex's jhin-A read on its own ~15.3-px squares (55 x 74, tools/art/design_jhin_hd.py: 74
    // rows / 41 = 1.805); every action Codex's whole-frame redraw of his old frame read onto it at the zoom its fit over
    // the old frame gives (tools/art/casts_jhin_hd.py, rig_jhin_hd.py; the attack, fourth shot, Q, W and R shot drawn from
    // their native body cells, the muzzle flashes and Q's throw flash baked on again by jhin_bake.json, the attack's shot
    // moved up to Codex's muzzle; his death's flung Whisper moved to where the old frames have it); 41 game px as his 1x
    // sprite, so no SIZES row
    ("league_jhin", 1.805, include_str!("../../../league/champions/league_jhin#anim.fanim")),
    // Kayn (2026-11-06, 「下面重做凯隐 维克托 永恩 泰坦」, 「凯隐本体 1.80 凯隐暗裔 1.79 凯隐影流 1.80 维克托 1.81 永恩2.20
    // 泰坦1.80」): Codex's kayn-A, kayn_darkin-A and kayn_shadow-A read on their own ~15.8 / 14.8 / 13-px squares (73 x 72,
    // 71 x 77, 104 x 72; tools/art/design_kayn*_hd.py); one sheet, one PPU: his three forms (rh_ Darkin, sh_ Shadow, the
    // wall shades w_ / rw_ / hw_) all at his 72 rows / 40 = 1.8 (the Darkin's 77 / 43 = 1.79 drawn 0.5 % small);
    // league_kayn_form renames the playing tag (rh_run ...) and the lookup takes its hd_ frames like any other; every
    // action Codex's whole-frame redraw of his old frame read onto its form's design at the zoom its fit over the old
    // frame gives (tools/art/casts_kayn_hd.py, rig_kayn_hd.py; Q's dash, W's winds and R's dive baked on again by
    // kayn_bake.json, the death's frames 6-8 dissolved with the old ordered dither); 40 game px as his 1x sprite, so no
    // SIZES row (the forms' own 1x sheets league_kayn_darkin / _shadow / *_wall are left as they are)
    ("league_kayn", 1.8, include_str!("../../../league/champions/league_kayn#anim.fanim")),
    // Viktor (the same release): Codex's viktor-A read on its own ~14.8-px squares (49 x 76, tools/art/design_viktor_hd.py:
    // 76 rows / 42 = 1.81); every action Codex's whole-frame redraw of his old frame read onto it at the zoom its fit
    // over the old frame gives (tools/art/casts_viktor_hd.py, rig_viktor_hd.py; nothing baked); 42 game px as his 1x
    // sprite, so no SIZES row
    ("league_viktor", 1.81, include_str!("../../../league/champions/league_viktor#anim.fanim")),
    // Yone (the same release): Codex's yone-A read on its own ~12.5-px squares (96 x 90, tools/art/design_yone_hd.py: 90
    // rows / 41 = 2.195); every action Codex's whole-frame redraw of his old frame read onto it at the zoom its fit over
    // the old frame gives (tools/art/casts_yone_hd.py, rig_yone_hd.py; E's cast baked on again into skill2_fx1 /
    // e_dash_fx1 by yone_bake.json); 41 game px as his 1x sprite, so no SIZES row
    ("league_yone", 2.195, include_str!("../../../league/champions/league_yone#anim.fanim")),
    // Nautilus (the same release): Codex's nautilus-A read on its own ~12.9-px squares (73 x 92,
    // tools/art/design_nautilus_hd.py: 92 rows / 51 = 1.804); every action Codex's whole-frame redraw of his old frame
    // read onto it at the template's squares (tools/art/casts_nautilus_hd.py, rig_nautilus_hd.py; the anchor's chain cut
    // where the old frames end it; nothing baked); 51 game px as his 1x sprite, so no SIZES row
    ("league_nautilus", 1.804, include_str!("../../../league/champions/league_nautilus#anim.fanim")),
];

/// Champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size): the anim tables' rects and
/// the texture's reported size are divided by PPU / size (hd_engine/src/lookup.rs: the cards, the encyclopedia, the
/// face icons, the BP slots draw him that much smaller, the UVs unchanged) and the battlefield scale is the game's / PPU
/// x size (hd_engine/src/view.rs), each about the frame's centre / the unit's position - so the hero's dense frames are
/// drawn lower by (1 / size - 1) x the pivot-to-soles distance and the soles stay where they were
/// (tools/art/ppu_gragas.py SHIFT).
/// Gragas: the user, 2026-10-12: 「酒桶模型缩小一点 太大了」 (85%), then 「要改全改啊」, then 80% (「怎么看起来还是比诺手高这么多」) (the cards and the encyclopedia too);
/// 2026-10-13 after the restyle 「酒桶可以稍微放大点吧 现在也太小了」 -> 90% from a size sheet, then 「还是太小啊」 -> 100% - judged on a preview GIF that
/// drew him at 80% - then 「感觉又太大了？」 from a true-scale sheet -> 90% (40 game px, Darius 42); his frames
/// lifted by the restyle (RESTYLE gragas lift_sq).
/// Zeri: 「等等泽丽感觉游戏里有点小」, picked 105% from the size sheet (drawn RAISE rows higher: tools/art/ppu_zeri.py).
/// Kassadin: 「在游戏太小了吧」, picked 115%, then 「感觉太大了点？调到110%差不多吧」 (41 game px); after the restyle
/// 「刀妹和卡萨丁感觉在游戏里偏大啊」 -> 100% (39 game px; RESTYLE kassadin lift_sq -3 undoes the rig's 110% raise) and Irelia
/// 115% -> 105% (44 game px with her blades); his hd frames drawn RAISE
/// rows higher (tools/art/rig_kassadin.py).
/// Braum: 「布隆做的也有点大 得缩小一点」 (85%), then 「稍微调大点」 (90%, 39 game px); after the restyle (a tenth
/// shorter) 「布隆也有这个看起来小的问题」 next to Alistar -> 105% (the user took the suggestion: 「按照你的建议选吧」).
/// His hd frames come SHIFT rows lower from tools/art/rig_braum.py (its 90%) and the restyle lifts them back
/// (tools/art/ppu_restyle.py RESTYLE braum lift).
/// Mordekaiser: the user picked 110% with a thicker outline (C, Kassadin's way), then 「铁男感觉做的太大了吧？」 -> 95%,
/// then 「铁男再稍微调大点」 -> 100%; then 「为什么模型看起来小啊 牛头那种就看起来很大」「铁男再游戏里还是过于高清」 ->
/// 115% at PPU 2.0 (1.74 squares a game pixel), his frames lifted by the restyle (RESTYLE mordekaiser lift).
/// Then 「铁男和布隆游戏里偏大了」: Mordekaiser 100 % (47 game px, Nautilus 51), Braum 95 % (39 px, 55 wide with his
/// shield), picked from a true-scale sheet; their frames moved down by the restyle (RESTYLE lift_sq).
/// Then on game 0.6.4 (2026-10-14) 「铁男模型太小」「铁男到110%吧」: Mordekaiser 110 % (52 game px).
/// Soraka: 「稍微变大点」 -> 110% (her frames lifted 3 squares: tools/art/ppu_restyle.py RESTYLE soraka).
/// Nilah: 「模型别太大 参考泽丽之前改过一版」 -> 90% from a size sheet (about 38 game rows with the blade's tip); her frames
/// lowered 3 squares by the restyle (RESTYLE nilah lift_sq).
/// Galio: PPU 2.0 at 85 % first (「这做的也太大了吧 缩小点模型」), then 「加里奥在局内看起来太小了」「而且在局内还是太高清了」 ->
/// 100 % at PPU 1.5 (tools/art/rig_galio.py dense), picked from true-scale sheets; then 「在局内还是偏小啊」 (38 game px
/// crown to soles, Darius 42) -> 110 % at PPU 1.65 (still 1.5 squares a game pixel), his dense frames drawn RAISE rows higher (rig_galio.py
/// SIZE / RAISE).
/// Corki: grown 1.2x by the restyle (「飞机像泽丽那样变大点」), then 「飞机在游戏里是不是偏大了？」 - 48 x 37 game px, as wide as
/// Garen and a solid lump - shown at 80 % (「到80%吧」, from a true-scale sheet), then 「太小了库奇 调到90%吧」 -> 90 %;
/// he flies, so his frames are not lowered.
/// Pantheon: 90 % for a while (「感觉模型太大了」「缩到90%」, his upright design idle 46 px), then his idle took Codex's crouched
/// ready stance like every action and he is 100 % again (「局内模型为什么变这么小了」: running 32-36 px against Darius's 41).
/// Malzahar: 115 % from the size sheet (all actions from the 3/4 front), drawn at PPU 2.2 first, then 「像素有点高 降低点需要」 ->
/// PPU 1.38 (1.2 squares a game pixel at 115 %); he floats, his frames lifted by the restyle (RESTYLE malzahar lift).
/// Wukong: 「猴子现在太小了」 (2026-10-20, 36 game px against Lee Sin's / Pantheon's / Garen's 41) -> 115 % from a
/// true-scale sheet (41 game px), his frames lifted 2 squares by the restyle (RESTYLE wukong lift_sq).
/// Nami: 90 % (the user, 2026-10-20: 「娜美的模型可以整体缩小一点 太大了」), her frames 2 squares lower (RESTYLE nami
/// lift_sq: 11.5 x 1.5 x (1 / 0.9 - 1) = 1.9) so her tail stays on the ground.
/// Hwei: 85 % (the user, 2026-10-22: 「画师局内有点大 可以调小一点」, 0.85 picked of 0.9 / 0.85 / 0.8), his frames 3 squares
/// lower (RESTYLE hwei lift_sq: 11.5 x 1.5 x (1 / 0.85 - 1) = 3.0).
/// K'Sante: 90 % (the user, 2026-10-22: 「奎桑提的模型在游戏局内也太大了」, 0.9 picked of 0.9 / 0.85 / 0.8), his frames 2
/// squares lower (RESTYLE ksante lift_sq: 11.5 x 1.2 x (1 / 0.9 - 1) = 1.5).
/// Warwick: 90 % (the user, 2026-10-23: 「狼人局内模型有点大了」 - 46 game px spike to soles), his frames 2 squares lower
/// (RESTYLE warwick lift_sq: 11.5 x 1.2 x (1 / 0.9 - 1) = 1.5).
/// Caitlyn: 90 % (the user, 2026-10-24: 「女警模型局内整体有点大 调小一点需要」 - 46 game px hat to soles, the tallest
/// marksman: Kai'Sa 43, Varus 45, Jinx 37), her frames 2 squares lower (RESTYLE caitlyn lift_sq: 11.5 x 1.45 x (1 / 0.9 - 1) = 1.9).
/// Ambessa: 85 % (the user, 2026-10-25: 「太大了安倍萨 整体模型缩小一点可以吗」 - 48 game px hair to soles with the two blades
/// out to 59; 85 % = 41, Darius's / Garen's 42, from a true-scale sheet), her frames 4 squares lower (RESTYLE ambessa
/// lift_sq: 11.5 x 2.0 x (1 / 0.85 - 1) = 4.1).
/// Zac: 85 % (the user, 2026-10-26: 「扎克的体型在这游戏里异常的大」 - 59 x 45 game px standing, as wide as Cho'Gath and
/// Sion, and 79 wide in his punch, 93 landing his E: the widest in the pack; 85 % picked from a true-scale sheet of 100 /
/// 90 / 85 / 80 %: 50 x 39 standing, 67 / 79 in the punch / E), his frames 3 squares lower (RESTYLE zac lift_sq:
/// 11.5 x 1.5 x (1 / 0.85 - 1) = 3.0).
/// Talon: 90 % (the user, 2026-10-31: 「男刀局内体型有点过大了 缩小一点」 - 39 game px hood to soles), his frames 2 squares
/// lower (RESTYLE talon lift_sq: 11.5 x 1.5 x (1 / 0.9 - 1) = 1.9).
pub const SIZES: &[(&str, f32)] = &[("league_gragas", 0.90), ("league_zeri", 1.05), ("league_kassadin", 1.00),
                                    ("league_braum", 0.95), ("league_mordekaiser", 1.10),
                                    ("league_irelia", 1.05), ("league_soraka", 1.10), ("league_galio", 1.10), ("league_nilah", 0.90),
                                    ("league_corki", 0.90), ("league_malzahar", 1.15), ("league_aphelios", 0.90),
                                    ("league_poppy", 0.85), ("league_yuumi", 0.75), ("league_wukong", 1.15),
                                    ("league_nami", 0.90), ("league_hwei", 0.85),
                                    ("league_ksante", 0.90), ("league_warwick", 0.90), ("league_caitlyn", 0.90),
                                    ("league_ambessa", 0.85),
                                    ("league_zac", 0.85), ("league_talon", 0.90)];

/// Heroes whose body grows with a stack: (id, the buff whose instances on him are the stacks, growth a stack).
/// Cho'Gath's Feast (the user, 2026-10-19: 「变大可以无限 加生命」): every champion it eats is one more Permanent
/// `league_chogath_r_stack` on him (+health, tools/kit/build_chogath.py r_stack_hp) and his body is drawn r_grow %
/// bigger a stack, with no cap, about his soles (hd_engine/src/view.rs: only the body's own commands, so his shadow and
/// rings stay). The main pack loses the stacks at his death (Permanent buffs end with it); the add-on league_chogath
/// puts them back. 15 % a stack (was 5 %: one bite put 2 game pixels on his 38, the user 2026-10-23: 「大虫子身体不变大」), then
/// 30 % a stack and at most twice his size (the user 2026-10-26 after a game with one bite, x1.15:
/// 「大虫子体型不变大？」「隔壁oppi的大虫子就会变大的」, picked 30 % / 2x), then the cap gone (the user 2026-10-31: 「大虫子体型应该可以无限变大吧」 - 4 of 45
/// logged games reached the 4 bites of x2, 1 had 5): one bite x1.3, four x2.2, ten x4. From the 5th bite half a step
/// (hd_engine's GROW_KNEE / GROW_TAIL; the user 2026-11-03: 「大虫子在局内后期变的有点太大了 稍微可以缩小一点」 - the watched game had
/// 9 bites, x3.7): five x2.35, nine x2.95, ten x3.1.
pub const GROWTH: &[(&str, &str, f32)] = &[("league_chogath", "league_chogath_r_stack", 0.30)];

/// Heroes drawn bigger while a buff of theirs is on them: (id, the buffs - any one of them, the size, seconds to grow
/// to it and to shrink back), about the soles like GROWTH, eased in and out (hd_engine's eased). Volibear's
/// Stormbringer (the user, 2026-11-01: 「开大时候可以加大点体型吧 我记得英雄联盟是这样的」): League's R makes him 35 % bigger, grown over 1.25
/// seconds from the cast and shrunk back when it ends - here from the leap (`league_volibear_r_air`, 1 s) through the
/// 12 s storm form after the landing (`league_volibear_r_form`), main pack data both. 1.35 at first; 1.15 at the user's
/// word (2026-11-02: 「开大模型变的实在太大了」 - 61 game px against Darius' and Garen's 42, his own 45 already the
/// tallest of them; 1.15: 52)
pub const FORMS: &[(&str, &[&str], f32, f32)] =
    &[("league_volibear", &["league_volibear_r_air", "league_volibear_r_form"], 1.15, 1.25)];

/// Effect sheets drawn dense like a hero's sheet (`idle` / `hd_idle` and any more tags, each with its hd_ twin; PPU squares
/// a game pixel, hd_idle PPU times as wide): league_heimerdinger's turrets, league_leblanc_clone (below) and the rest
/// (league_zyra_thicket was one until 2026-10-21, now a plain 1x sheet: 「婕拉的大招特效局内怎么这么模糊」; league_yuumi_ride,
/// the cat on the head of the ally Yuumi rides, until 2026-11-05 - see DRAWN_EFFECTS). Looked up like the heroes
/// (hd_engine/src/lookup.rs); the battlefield's entity scale (hd_engine/src/view.rs) never meets them - they are no
/// entity's body.
pub const EFFECTS: &[(&str, f32, &str)] = &[
    // league_heimerdinger's two turrets (Q's and R's apex), one life each, drawn from their step-1 designs at his 1.5
    // (tools/art/import_heimerdinger_fx.py)
    ("league_heimerdinger_turret", 1.5, include_str!("../../../league/effects/league_heimerdinger_turret#anim.fanim")),
    ("league_heimerdinger_apex", 1.5, include_str!("../../../league/effects/league_heimerdinger_apex#anim.fanim")),
    // and the same seen from the side for league_heimerdinger's add-on (it picks the side its target is on; the user:
    // 「炮台改成侧面朝敌人」「灵活利用PPU 炮也可以调的清晰」「炮太高清了 降低点像素」): League's models at PPU 1.75, a
    // little finer than his 1.5 (tools/art/design_heimerdinger_side_turrets.py)
    ("league_heimerdinger_turret_r", 1.75, include_str!("../../../league/effects/league_heimerdinger_turret_r#anim.fanim")),
    ("league_heimerdinger_turret_l", 1.75, include_str!("../../../league/effects/league_heimerdinger_turret_l#anim.fanim")),
    ("league_heimerdinger_apex_r", 1.75, include_str!("../../../league/effects/league_heimerdinger_apex_r#anim.fanim")),
    ("league_heimerdinger_apex_l", 1.75, include_str!("../../../league/effects/league_heimerdinger_apex_l#anim.fanim")),
    // league_leblanc's passive clone (Mirror Image): her own dense idle where she stood, then the blink-out column - drawn
    // at her PPU 2.0 like her body (the user: 「妖姬有点bug吧 分身怎么不是高清帧啊 被动的」; tools/fix/leblanc_clone_hd.py);
    // at her size only since it is a DRAWN_EFFECTS row (0.9.14) - until then twice it
    // league_ivern's Daisy (R): her rise, punch, slam and goodbye, each its own dense sheet (one life a sheet, the
    // turrets' way), drawn from her step-1 design uncut at PPU 1.9 (the user: 「小菊用不裁的原样（D-full，PPU 1.9）」;
    // tools/art/rig_ivern.py). Drawn at 1 / PPU only since the effect draw shrinks her (DRAWN_EFFECTS, 2026-10-27): at 1.9
    // and then 2.533 she stood 76 game px, a square a pixel (「这是修复了？」); 1.333 = 75 % of that
    ("league_ivern_daisy_drop", 1.333, include_str!("../../../league/effects/league_ivern_daisy_drop#anim.fanim")),
    ("league_ivern_daisy_punch", 1.333, include_str!("../../../league/effects/league_ivern_daisy_punch#anim.fanim")),
    ("league_ivern_daisy_slam", 1.333, include_str!("../../../league/effects/league_ivern_daisy_slam#anim.fanim")),
    ("league_ivern_daisy_bye", 1.333, include_str!("../../../league/effects/league_ivern_daisy_bye#anim.fanim")),
    // league_illaoi's tentacle (her passive, W, R): one life on the spot it grew (rising, swaying, sinking back) and the
    // lash slamming down on the unit it strikes, each its own dense sheet, drawn from its step-1 design at PPU 1.5 (the
    // user: 「触手 44」; tools/art/rig_illaoi.py)
    ("league_illaoi_tentacle", 1.5, include_str!("../../../league/effects/league_illaoi_tentacle#anim.fanim")),
    ("league_illaoi_lash", 1.5, include_str!("../../../league/effects/league_illaoi_lash#anim.fanim")),
    // league_azir's summons (tools/art/rig_azir.py, the user's picks: 「召唤物照图」): the sand soldier from the front (each
    // slot's standing stamp and its rise out of the sand), the Imperial Guards' wall from the side (right-facing and the
    // mirrored left-facing tags: the add-on picks one by the wall's direction) and the Sun Disc (its rise and its stamp),
    // drawn from their step-1 designs at his 1.5
    ("league_azir_soldier", 1.429, include_str!("../../../league/effects/league_azir_soldier#anim.fanim")),
    ("league_azir_guard", 1.5, include_str!("../../../league/effects/league_azir_guard#anim.fanim")),
    ("league_azir_disc", 1.5, include_str!("../../../league/effects/league_azir_disc#anim.fanim")),
    // the sand soldiers (front and side) at 1.429 = 1 / 0.7: 70 % of the 54 game px they stood at a square a pixel, before
    // the effect draw shrank them (DRAWN_EFFECTS; the user, 2026-10-25: 「沙皇的沙兵游戏里这么大？得缩小一点吧」 - 2.143 =
    // 1.5 / 0.7 changed nothing on screen, 2026-10-27: 「沙皇同理和没修复之前没区别」)
    // the add-on's sand soldier from the side (the user: 「沙兵没攻击动作 ... 还有不面向敌人」; tools/art/
    // design_azir_side_soldier.py, from League's model): standing, rising and stabbing, right and left
    ("league_azir_soldier_side", 1.429, include_str!("../../../league/effects/league_azir_soldier_side#anim.fanim")),
    ("league_leblanc_clone", 2.0, include_str!("../../../league/effects/league_leblanc_clone#anim.fanim")),
    // league_zoe's stolen summoner spells (the add-on plays them; tools/art/draw_zoe_spells.py): their own pictures at
    // PPU 2 and League's icons at 3 (32 squares of the client's 64-px icon still read, 22 did not) - many tags each,
    // every one with its hd_ twin
    ("league_zoe_spells", 2.0, include_str!("../../../league/effects/league_zoe_spells#anim.fanim")),
    ("league_zoe_spell_icons", 3.0, include_str!("../../../league/effects/league_zoe_spell_icons#anim.fanim")),
    // league_zaahen's revive (the add-on banishes him while he rises again, so his rising is an effect picture): his
    // frames over the light column at his own 1.75, facing right and left (tools/art/rig_zaahen.py --rise; the add-on
    // plays the side facing the nearest enemy champion: an effect picture is never mirrored); at his size only since it
    // is a DRAWN_EFFECTS row (0.9.14) - until then 1.75 times it
    ("league_zaahen_rise", 1.75, include_str!("../../../league/effects/league_zaahen_rise#anim.fanim")),
    // league_karthus's spirit (0.5.0, the user 2026-11-03: 「死了灵体还能移动 还能有残血？」「这能和英雄联盟一样吗」): the
    // add-on banishes him for the whole of it, so his ghost is the banish's picture - his own idle_base squares at his
    // 1.5 in a pale glowing green, facing right and left (tools/art/draw_karthus_ghost.py)
    ("league_karthus_ghost", 1.5, include_str!("../../../league/effects/league_karthus_ghost#anim.fanim")),
];

/// Effects whose pictures the view node draw (hd_engine/src/view.rs effect_detour) shrinks to 1 / PPU about their
/// top-left corner. Every other EFFECTS sheet is still drawn a square a game pixel (its frames' corners placed at
/// 1 / PPU) - the way the user has seen them; Daisy and the sand soldiers were 76 / 54 game px that way (the user,
/// 2026-10-27: 「给召唤物做真正的缩放，保留高清，大小按我看到的再缩一点」).
/// league_zoe's stolen summoner spells and their icons too (0.9.3, the user, 2026-11-03: 「大橙圈是召唤师技能屏障特效 你
/// 弄的太大了吧」「还有地上的召唤师技能图标也太大了吧」): registered at PPU 2 and 3 on 10-22 but never listed here, the
/// game drew Barrier's shell 88 x 104 px (designed 44 x 52, three times her height) and a shard's icon 34 px (Zoe's
/// own height, designed 11), each hanging right and down from its spot. league_karthus's ghost (0.9.5) from the start.
/// Only pictures the view node draw draws pass here: the kits' view effects (`view_effects`), played at a point or
/// following a unit. A following one passes too: Daisy's four pictures all follow the champion her R lands on
/// (`"is_follow": true`) and the 11-06 log has an "effect picture drawn" line for each (league.prev.log 534.09-536.11);
/// the body draw calls the node draw (hd_engine build.rs effect_draw), and inside a dense hero's body draw hd_engine's
/// cmd_kind keeps the effect's own 1 / PPU (view.rs unshrink_extras brings the extras back to the game's size round it).
/// A BUFF's view (`view_buffs`) is drawn elsewhere and never shrunk: the dense texels a square a game pixel about the
/// 1 / PPU corner, PPU times too big and hanging right and down, whatever this table says. league_yuumi_ride (the cat on
/// the head of the ally Yuumi rides, a buff's view) was listed here from 0.9.6 (the user, 2026-11-03: 「悠米还是会遮挡很多
/// 英雄的脸部」 - drawn 21 x 26 for the user's 14 game px, its bottom 7 px under the crown its lift was measured for and 4 px
/// right of the host's middle) and changed nothing: the 11-05 log had the sheet loaded and Yuumi riding, and no "effect
/// picture drawn" line for it. league_zoe's buff pictures the same (its 1x sheet league_zoe_spells_1x). So (0.9.12,
/// 2026-11-05) the cat is a plain 1x sheet, league_yuumi_ride_1x, that the game draws itself, centred on the host: not
/// registered at all.
/// league_leblanc_clone and league_zaahen_rise (0.9.14, 2026-11-06, found with Yone's left body): the hero himself on an
/// effect sheet at his own PPU - LeBlanc's passive clone where she stood (the kit's league_leblanc_p_clone, a
/// CasterViewEffect at a point: her own 31 x 63 idle, dense 62 x 128) and Zaahen rising again inside the add-on's banish
/// (league_zaahen_rv_rise_r / _l, the banish's picture following him, Karthus's ghost's way: 73 x 117 with the light
/// column, dense 128 x 205). Unlisted, both were drawn a square a game pixel: the clone twice her size, the risen Zaahen
/// 1.75 times his, hanging right and down from the corner. Listed, they come out at the hero's size (neither hero has a
/// SIZES row): test a_heros_figure_on_an_effect_sheet_is_drawn_at_his_size.
/// league_yone - a hero's own sheet (the user, 2026-11-06: 「永恩有bug吧放完E技能后模型变大？」): Spirit Cleave leaves his
/// body where he cast it, the kit's view league_yone_e_body - tag e_body of his own sheet, played at that point (the end
/// of the anchor projectile) for its 4 s until the spirit snaps back. Dense since his PPU redo (#694), the node draw drew
/// it a square a game pixel: a 59 x 145 game px frame for his 27 x 66 (the figure 100 px tall, he is 43-46), its
/// top-left corner where the 1x frame's is, so hanging right and down, its feet 55 px under the ground. Listed here,
/// every picture the node draw makes of his sheet is shrunk to 1 / PPU; his body never passes there (the body draw
/// draws it itself, from the battlefield table). A hero's own sheet goes here only when its kit plays it at points
/// alone (a view following his own unit is drawn inside his body draw, where unshrink_extras takes his own sheet for
/// his body) and he has no SIZES row (the shrink is 1 / PPU, the table's rects / PPU x size): tests
/// a_heros_own_sheet_is_a_drawn_effect_only_at_points, yones_left_body_is_drawn_at_his_size.
/// league_reksai (0.9.14) the same way: the add-on's tunnel plays her own t_dig / t_up (and the mirrored _l) at the
/// tunnel's mouths (the kit's league_reksai_t_dig ... views, not following), dense at 1.2 - drawn 1.2 times her size
/// until now. Every kit's view of a dense hero's own sheet must be listed here: test
/// every_view_of_a_dense_heros_own_sheet_is_drawn_at_his_size.
pub const DRAWN_EFFECTS: &[&str] = &["league_ivern_daisy_drop", "league_ivern_daisy_punch", "league_ivern_daisy_slam",
                                     "league_ivern_daisy_bye", "league_azir_soldier", "league_azir_soldier_side",
                                     "league_zoe_spells", "league_zoe_spell_icons", "league_karthus_ghost",
                                     "league_yone", "league_reksai", "league_leblanc_clone", "league_zaahen_rise"];

/// Tall heroes drawn smaller wherever the UI draws lo_ frames (the ban/pick card above all): the card's canvas holds
/// about 40 game px at 2.2x and these idles are 45-58 px from the head to the feet, so the knees and feet hid behind
/// the name bar (the user, 2026-10-19: 「烈娜塔在BP格位置调一下吧 一半的腿 还有其他英雄也有这情况」, picked the
/// whole-body mock). Size = 39 / the idle's height, every HD hero whose card hid 6 px or more
/// (tools/art/bp_card_audit.py --legs); their banpick_center y set for that size. 1x heroes have no lo_ frames: not here.
pub const UI_SIZES: &[(&str, f32)] = &[
    ("league_camille", 0.82),
    ("league_cassiopeia", 0.85),
    ("league_drmundo", 0.87),
    ("league_elise", 0.80),
    ("league_galio", 0.67),
    ("league_janna", 0.81),
    ("league_jayce", 0.78),
    ("league_mordekaiser", 0.74),
    ("league_morgana", 0.84),
    ("league_nami", 0.76),
    ("league_nasus", 0.85),
    ("league_nidalee", 0.87),
    ("league_rell", 0.85),
    ("league_renata", 0.78),
    ("league_tahmkench", 0.87),
    // Zyra (#140): 43.5 game rows hair to soles at PPU 1.7 - 12.7 px of her legs hid under the card's canvas
    ("league_zyra", 0.89),
    // Warwick (#142): 63 game px wide with his raised tail (94 squares at PPU 1.5) - the tail's tip and the far claws ran
    // past the card's 59.5 px canvas
    ("league_warwick", 0.88),
    // Mel (#144): 43.3 game rows bun top to soles at PPU 1.5 - 12.7 px of her heels and train hid under the card's canvas
    ("league_mel", 0.90),
    // Aurora: about 48 game px from her ear tips to her soles at PPU 2.25 (the long ears 10 over the hat) - at -12 the card
    // cut 22 px of her ears, at the rule's -1 her legs hid; 0.82 with banpick_center -9: the ear tips 3 px under the
    // canvas top, the soles on its bottom (bp_card_audit.py)
    ("league_aurora", 0.82),
    // Nunu & Willump: 46 game px from Nunu's pompom to Willump's soles at PPU 1.37 - at -12 the card cut 20 px of them, at
    // the rule's -2 Willump's feet hid under the name bar; 0.85 with the card value bp_card_audit.py gives: the pompom
    // under the canvas top, the soles on its bottom
    ("league_nunu", 0.85),
    // Azir: about 49 game px from his sceptre's tip to his soles at PPU 1.5 (the crest 38) - 39 / 49 = 0.80
    ("league_azir", 0.80),
    // Zac: 46.7 game px from his tendril tip to his soles over the idle reel (the punch's wind-up reaches higher) at PPU
    // 1.5 - at the placeholder -8 the card cut 6 px of the tendril and hid 4 px of his feet; 0.84 with the card value
    // bp_card_audit.py gives: the tendril under the canvas top, the soles on its bottom; 0.99 since his frames are drawn at
    // 85 % (SIZES, 2026-10-26): 0.84 / 0.85, the card as before
    ("league_zac", 0.99),
    // Singed: 45 game px from the tank's cap to his soles at PPU 1.39, the idle reel's raised flask higher; UI size and
    // card value set with bp_card_audit.py (the tank under the canvas top, the soles on its bottom)
    ("league_singed", 0.80),
    // Bel'Veth: 47 game px from her shoulder spikes to her claws at PPU 1.75 (the raised wings of the reel higher); UI
    // size and card value set with bp_card_audit.py
    ("league_belveth", 0.82),
    // Taliyah: 40 game px from her piled hair to her soles at PPU 1.75 (shorter than Bel'Veth: 0.82 left her head 15 px
    // under the card's top); UI size 0.98 and card value -10 set with bp_card_audit.py
    ("league_taliyah", 0.98),
    // Aurelion Sol: 44 game px from his crest to his tail tip at PPU 1.75, hovering 2 more; UI size and card value set
    // with bp_card_audit.py (-3: the raised claw of the idle reel's attack snippet stays on the card)
    ("league_aurelionsol", 0.86),
    // Kled: 41 game px from his hat spike to Skaarl's claws at PPU 2.0 (the idle reel's raised axe higher); UI size and
    // card value set with bp_card_audit.py
    ("league_kled", 0.95),
    // Yorick: 48 game px from his shovel's tip to his boots at PPU 1.75 (39 / 48); UI size and card value set with
    // bp_card_audit.py. 0.81 / -1 put the shovel's tip on the canvas top and hid 8.7 px of his legs under the name
    // (the user, 2026-10-25: 「约里克BP界面位置不对」): 0.76 / -11 - hood to boots on the card, the thin tip over the top
    ("league_yorick", 0.76),
    // Ambessa: 48 game px from her hair to her soles at PPU 2.0 (39 / 48; the blades out to 59 px wide); UI size and card
    // value set with bp_card_audit.py. The card's -4 fitted the idle's raised blades and, with her 85 % (SIZES) in the
    // lo_ frames, hid 6 px of her legs under the name (the user, 2026-10-27, after K'Sante's: 「安倍萨也有这问题？」):
    // -10 - hair to soles on the card, the raised blades' tips over the top
    ("league_ambessa", 0.81),
    // Trundle: 42.5 game px from his mane to his feet at PPU 2.0 but 52 wide with the ice club (the card's canvas is 59.5):
    // at 1.0 the club and his feet ran off the card; UI size and card value set with bp_card_audit.py
    ("league_trundle", 0.82),
    // Locke: 44 game px from his hair to his soles at PPU 2.0 (the card's canvas is 40 tall), the case swung out in his
    // ult; UI size and card value set with bp_card_audit.py
    ("league_locke", 0.85),
    // Zaahen: 48 game px from his horn tips to his soles at PPU 1.75 (the card's canvas is 40 tall), 50 wide with the
    // glaive across him and the wings, the glaive raised high in his attack and Q; UI size and card value set with
    // bp_card_audit.py
    ("league_zaahen", 0.78),
    // K'Sante: 45 game px from his hair and the two Ntofos' heads to his soles (lo_idle, his 90 % SIZES in it), 46 wide
    // with the Ntofos on both sides - at 1.0 / -6 he filled the card and 7 px of his legs hid under the name (the user,
    // 2026-10-27: 「奎桑提在BP格太大了吧 学学其他英雄怎么缩放的」); 0.82 with -10 as Ambessa's / Trundle's / Bel'Veth's:
    // hair to soles on the card with 4 px over him, only the raised Ntofo of the reel's attack snippet over the top
    ("league_ksante", 0.82),
];

/// This pack's table, as league.dll hands it to hd_engine at init (src/lib.rs).
pub fn table() -> Table<'static> {
    Table {
        pack: crate::ID,
        heroes: HEROES.to_vec(),
        sizes: SIZES.to_vec(),
        growth: GROWTH.to_vec(),
        forms: FORMS.iter().map(|&(id, buffs, size, secs)| (id, buffs.to_vec(), size, secs)).collect(),
        effects: EFFECTS.to_vec(),
        drawn_effects: DRAWN_EFFECTS.to_vec(),
        ui_sizes: UI_SIZES.to_vec(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use hd_engine::hd::{checks, Heroes, UI_PPU};

    #[test]
    fn heroes_are_found_by_id_and_resource_name() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/league/champions/{id}#anim")).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/base/aseprite_resources/champions/{id}#sheet")).map(|x| x.id), Some(id));
        }
        assert!(h.get("league_amumu").is_none());
        // the tft pack's heroes are its own table's (tft/src/hd.rs): tft.dll hands them to whichever DLL hosts
        assert!(h.get("tft_powder").is_none());
        assert!(h.of_name("asset/base/aseprite_resources/champions/alchemist#anim").is_none());
        assert!(h.of_name("asset/league/champions/league_ashe_fx#sheet").is_none());
        assert!(h.of_name("").is_none());
    }

    #[test]
    fn every_registered_sheet_is_ppu_times_as_wide() {
        checks::every_registered_sheet_is_ppu_times_as_wide(&table());
    }

    #[test]
    fn every_registered_sheet_has_hd_tags_for_all_its_tags() {
        checks::every_registered_sheet_has_hd_tags_for_all_its_tags(&table());
    }

    #[test]
    fn ui_sizes_shrink_heroes_with_lo_frames() {
        checks::ui_sizes_shrink_heroes_with_lo_frames(&table());
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.get("league_zoe").map(|x| x.ui), Some(UI_PPU));
        // the face crops keep the plain UI size, so a hero's face point holds there too
        let galio = h.get("league_galio").unwrap();
        assert_eq!(galio.ui_for(false), UI_PPU);
        assert!(galio.ui_for(true) > UI_PPU);
    }

    #[test]
    fn effect_sheets_have_a_dense_idle() {
        checks::effect_sheets_have_a_dense_idle(&table());
    }

    #[test]
    fn every_row_is_one_of_the_packs_heroes_once() {
        checks::ids_are_the_packs_once(&table());
    }

    #[test]
    fn the_table_reaches_a_host_unchanged() {
        checks::the_table_goes_through_the_text_unchanged(&table());
    }

    /// Cho'Gath's Feast (the growth row) and the shrunk effects reach the engine's registered heroes.
    #[test]
    fn the_growth_and_drawn_effects_go_with_the_table() {
        assert!(GROWTH.iter().any(|g| g.0 == "league_chogath" && g.1 == "league_chogath_r_stack"));
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.growth, GROWTH.to_vec());
        assert_eq!(h.forms, FORMS.to_vec());
        assert_eq!(h.drawn_effects, DRAWN_EFFECTS.to_vec());
        assert_eq!(h.packs, vec!["league"]);
    }

    /// Volibear's form row (hd_engine's eased): his leap and storm form are main pack buffs of his, and a hero grows
    /// one way (a stack or a form).
    #[test]
    fn volibear_grows_in_his_form() {
        let data = include_str!("../../../league/champion/league_volibear.data_champion");
        let (_, buffs, s, t) = *FORMS.iter().find(|f| f.0 == "league_volibear").expect("Volibear grows in his form");
        assert_eq!((s, t), (1.15, 1.25));
        for b in buffs {
            assert!(data.contains(&format!("\"name\": \"{b}\"")), "the main pack never gives him {b}");
        }
        assert!(FORMS.iter().all(|f| !GROWTH.iter().any(|g| g.0 == f.0)), "a hero grows one way");
    }

    /// The text of every flat object (no brace inside it: a view, a ViewEffect) of a .data_champion holding `needle`.
    fn objects_with(data: &str, needle: &str) -> Vec<String> {
        data.match_indices(needle)
            .map(|(at, _)| {
                let open = data[..at].rfind('{').expect("an object");
                let close = at + data[at..].find('}').expect("an object");
                data[open..=close].to_string()
            })
            .collect()
    }

    /// The views of `id`'s kit (`data`: its .data_champion) drawn from its own sheet.
    fn own_sheet_views(id: &str, data: &str) -> Vec<String> {
        objects_with(data, &format!("\"anim\": \"asset/league/champions/{id}\""))
    }

    /// A hero's own sheet in DRAWN_EFFECTS: the node draw shrinks every picture of it to 1 / PPU, so its kit plays it at
    /// points only (a view following his own unit is drawn inside his body draw, where hd_engine's unshrink_extras takes
    /// his own sheet for his body and the shrink pair for extras: PPU times big again) and the hero has no SIZES row (the
    /// shrink is 1 / PPU, the table's rects are divided by PPU / size).
    #[test]
    fn a_heros_own_sheet_is_a_drawn_effect_only_at_points() {
        for &id in DRAWN_EFFECTS.iter().filter(|id| HEROES.iter().any(|h| h.0 == **id)) {
            assert!(!SIZES.iter().any(|s| s.0 == id), "{id}: a SIZES row - the node draw's 1 / PPU would miss it");
            let path = format!("{}/../../league/champion/{id}.data_champion", env!("CARGO_MANIFEST_DIR"));
            let data = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
            let views = own_sheet_views(id, &data);
            assert!(!views.is_empty(), "{id}: no view of its kit drawn from its own sheet - nothing to shrink");
            for v in &views {
                assert!(!v.contains("\"is_follow\": true"), "{id}: a view of its own sheet follows a unit: {v}");
            }
        }
    }

    /// Yone's Spirit Cleave leaves his body behind as a picture of his own sheet played at a point (the kit's
    /// league_yone_e_body, tag e_body): dense since #694, it was drawn a square a game pixel, 2.195 times his size (the
    /// user, 2026-11-06: 「永恩有bug吧放完E技能后模型变大？」); listed in DRAWN_EFFECTS the node draw shrinks it to his size.
    #[test]
    fn yones_left_body_is_drawn_at_his_size() {
        assert!(DRAWN_EFFECTS.contains(&"league_yone"));
        let data = include_str!("../../../league/champion/league_yone.data_champion");
        let views = own_sheet_views("league_yone", data);
        assert_eq!(views.len(), 1, "{views:?}");
        assert!(views[0].contains("\"name\": \"league_yone_e_body\"") && views[0].contains("\"tag\": \"e_body\""));
        // played by E (a ViewEffect: at the anchor's end, a point) and his sheet has its dense frames
        let plays = objects_with(data, "\"name\": \"league_yone_e_body\"");
        assert!(plays.iter().any(|o| o.contains("\"type\": \"ViewEffect\"")), "{plays:?}");
        let (_, ppu, fanim) = *HEROES.iter().find(|h| h.0 == "league_yone").unwrap();
        assert!(hd_engine::hd::hd_tags(fanim).contains(&"hd_e_body".to_string()));
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.get("league_yone").map(|x| x.shown()), Some(ppu));
        assert!(h.drawn_effects.contains(&"league_yone"));
        // the add-on's copy of him (league_yone_r, made from the main pack) plays the same picture
        let addon = include_str!("../../league_yone_r/override/league_yone.data_champion");
        assert_eq!(own_sheet_views("league_yone", addon), views);
    }

    /// The kit sections a view can sit in, and the one an anim at byte `at` of a .data_champion belongs to.
    fn section_at(data: &str, at: usize) -> &'static str {
        ["view_effects", "view_buffs", "view_projectiles"]
            .into_iter()
            .filter_map(|s| data[..at].rfind(&format!("\"{s}\"")).map(|p| (p, s)))
            .max()
            .map_or("?", |(_, s)| s)
    }

    /// Every kit the game can load (the main pack's and every add-on's override copy) with its path.
    fn every_kit() -> Vec<(String, String)> {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let mut dirs = vec![root.join("league/champion")];
        for addon in std::fs::read_dir(root.join("addons")).expect("addons/").flatten() {
            dirs.push(addon.path().join("override"));
        }
        let mut kits = Vec::new();
        for dir in dirs {
            let Ok(files) = std::fs::read_dir(&dir) else { continue };
            for f in files.flatten().map(|f| f.path()).filter(|p| p.extension().is_some_and(|e| e == "data_champion")) {
                let text = std::fs::read_to_string(&f).unwrap_or_else(|e| panic!("{}: {e}", f.display()));
                kits.push((f.display().to_string(), text));
            }
        }
        assert!(kits.len() > 150, "{} kits found", kits.len());
        kits
    }

    /// A view of a dense hero's own sheet is drawn by the view node draw a square a game pixel, PPU times his size, unless
    /// the hero is in DRAWN_EFFECTS (Yone's left body, Rek'Sai's tunnel mouths, 2026-11-06); and only a view effect played
    /// at a point gets there (a buff's view never does, a following one would be drawn in his own body draw).
    #[test]
    fn every_view_of_a_dense_heros_own_sheet_is_drawn_at_his_size() {
        const NEEDLE: &str = "\"anim\": \"asset/league/champions/";
        let mut seen = Vec::new();
        for (path, data) in every_kit() {
            for (at, _) in data.match_indices(NEEDLE) {
                let rest = &data[at + NEEDLE.len()..];
                let id = &rest[..rest.find('"').expect("a closed string")];
                if !HEROES.iter().any(|h| h.0 == id) {
                    continue;
                }
                let view = &data[data[..at].rfind('{').unwrap()..at + data[at..].find('}').unwrap()];
                assert_eq!(section_at(&data, at), "view_effects", "{path}: {id}'s own sheet outside the view effects: {view}");
                assert!(!view.contains("\"is_follow\": true"), "{path}: {id}'s own sheet following a unit: {view}");
                assert!(DRAWN_EFFECTS.contains(&id), "{path}: {id}'s own sheet played as a view, {id} not in DRAWN_EFFECTS");
                if !seen.iter().any(|s| s == id) {
                    seen.push(id.to_string());
                }
            }
        }
        // the scan finds the two known ones (2026-11-06)
        for id in ["league_reksai", "league_yone"] {
            assert!(seen.iter().any(|s| s == id), "{id} not found among {seen:?}");
        }
    }

    /// Rek'Sai's tunnel (the add-on league_reksai, 0.1.2): her own dig and rise frames played at the tunnel's mouths - at
    /// points, from her dense sheet at 1.2; listed in DRAWN_EFFECTS they come out at her size (they were 1.2 times it).
    #[test]
    fn reksais_tunnel_mouths_are_drawn_at_her_size() {
        assert!(DRAWN_EFFECTS.contains(&"league_reksai"));
        assert!(!SIZES.iter().any(|s| s.0 == "league_reksai"));
        let data = include_str!("../../../league/champion/league_reksai.data_champion");
        let views = own_sheet_views("league_reksai", data);
        let (_, ppu, fanim) = *HEROES.iter().find(|h| h.0 == "league_reksai").unwrap();
        let hd = hd_engine::hd::hd_tags(fanim);
        for tag in ["t_dig", "t_dig_l", "t_up", "t_up_l"] {
            assert_eq!(views.iter().filter(|v| v.contains(&format!("\"tag\": \"{tag}\""))).count(), 1, "{tag}: {views:?}");
            assert!(hd.contains(&format!("hd_{tag}")), "{tag}: no dense frames");
        }
        assert_eq!(views.len(), 4, "{views:?}");
        assert!(views.iter().all(|v| v.contains("\"is_follow\": false")), "{views:?}");
        assert_eq!(Heroes::of(&[&table()]).get("league_reksai").map(|x| x.shown()), Some(ppu));
        // the add-on's copy plays the same pictures
        let addon = include_str!("../../league_reksai/override/league_reksai.data_champion");
        assert_eq!(own_sheet_views("league_reksai", addon), views);
    }

    /// The first frame's (w, h) of tag `t` in a .fanim.
    fn first_frame(fanim: &str, t: &str) -> (f32, f32) {
        let at = fanim.find(&format!("\"{t}\"")).unwrap_or_else(|| panic!("no {t}"));
        let num = |key: &str| -> f32 {
            let k = at + fanim[at..].find(&format!("\"{key}\"")).unwrap() + key.len() + 2;
            let s = fanim[k..].trim_start().trim_start_matches(':').trim_start();
            s[..s.find(|c: char| !(c.is_ascii_digit() || c == '.')).unwrap()].parse().unwrap()
        };
        (num("w"), num("h"))
    }

    /// A hero himself on an effect sheet at his own PPU - LeBlanc's passive clone, Zaahen rising again, Karthus's ghost -
    /// is shrunk by the node draw to his size (none of them has a SIZES row): the sheet in DRAWN_EFFECTS at the hero's
    /// PPU. Unlisted, the clone was drawn twice LeBlanc's size and the risen Zaahen 1.75 times his (2026-11-06).
    #[test]
    fn a_heros_figure_on_an_effect_sheet_is_drawn_at_his_size() {
        for (sheet, hero) in [("league_leblanc_clone", "league_leblanc"), ("league_zaahen_rise", "league_zaahen"),
                              ("league_karthus_ghost", "league_karthus")] {
            let (_, ppu, _) = *EFFECTS.iter().find(|e| e.0 == sheet).unwrap_or_else(|| panic!("{sheet}"));
            let (_, hero_ppu, _) = *HEROES.iter().find(|h| h.0 == hero).unwrap_or_else(|| panic!("{hero}"));
            assert!(DRAWN_EFFECTS.contains(&sheet), "{sheet}: drawn PPU times big");
            assert_eq!(ppu, hero_ppu, "{sheet}: not at {hero}'s density");
            assert!(!SIZES.iter().any(|s| s.0 == hero), "{hero}: a SIZES row - 1 / PPU would not be his size");
        }
        // the clone is her own idle: the same 1x frame as hers
        let clone = EFFECTS.iter().find(|e| e.0 == "league_leblanc_clone").unwrap().2;
        let leblanc = HEROES.iter().find(|h| h.0 == "league_leblanc").unwrap().2;
        assert_eq!(first_frame(clone, "idle"), first_frame(leblanc, "idle"));
        // played at a point (her kit's passive, a CasterViewEffect) and inside a banish following him (the add-on's copy
        // of Zaahen), like Karthus's ghost
        let lb = include_str!("../../../league/champion/league_leblanc.data_champion");
        let clone_view = objects_with(lb, "\"anim\": \"asset/league/effects/league_leblanc_clone\"");
        assert_eq!(clone_view.len(), 1, "{clone_view:?}");
        assert!(clone_view[0].contains("\"is_follow\": false"));
        let plays = objects_with(lb, "\"name\": \"league_leblanc_p_clone\"");
        assert!(plays.iter().any(|o| o.contains("\"type\": \"CasterViewEffect\"")), "{plays:?}");
        let zaahen = include_str!("../../league_zaahen/override/league_zaahen.data_champion");
        let rise = objects_with(zaahen, "\"anim\": \"asset/league/effects/league_zaahen_rise\"");
        assert_eq!(rise.len(), 2, "{rise:?}");
        assert!(rise.iter().all(|v| v.contains("\"is_follow\": true")), "{rise:?}");
        let karthus = include_str!("../../league_karthus/override/league_karthus.data_champion");
        let ghost = objects_with(karthus, "\"anim\": \"asset/league/effects/league_karthus_ghost\"");
        assert!(ghost.len() == 2 && ghost.iter().all(|v| v.contains("\"is_follow\": true")), "{ghost:?}");
    }
}
