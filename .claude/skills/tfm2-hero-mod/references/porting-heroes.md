# Porting heroes from another MOBA (League of Legends, Dota 2, ...)

The two principles every successful pack writes in its description:

1. Kits are "rebalanced and readjusted towards TFM2 data availability" - keep the hero's
   *fantasy* (what fans recognise) and rebuild the numbers inside base-game ranges.
2. "Will only be making heroes that is currently possible" - skip heroes whose identity depends
   on something the data format cannot express.

## Slot mapping

| Source game | TFM2 |
|---|---|
| League of Legends: passive + Q W E R | two basics -> `skill` / `skill2`, R -> `ult`; fold the third basic and the passive in (see below) |
| Dota 2: 3 basics + ultimate (+ facets/aghs) | pick the 2 most iconic basics |

Roles: tank / fighter -> `Melee` (tags `Tank`, `CC`), assassin -> `Assassin`,
mage -> `Magician`, marksman -> `Range`, support -> `Util`.

TFM2 is auto-battled: the AI decides when to cast. Design every skill so that casting it
whenever a valid target is in `range` is reasonable; mechanics that rely on player timing
(combos, cancels, precise recasts, positioning tricks) must become automatic.

## Mechanic -> effect mapping

OK = direct, ~ = approximate, X = not possible in data-only mods.

| Source mechanic | TFM2 implementation | |
|---|---|---|
| Line skillshot | `LinearProjectile` (penetrate true/false) | OK |
| Targeted missile | `TargetProjectile` | OK |
| Ground AoE with delay / lob | `RangeProjectile`, `ParabolicProjectile`, `Delayed`+`RangeEffect` | OK |
| Lingering field (blizzard, fire rain) | `RangePeriodProjectile` | OK |
| Aura around self | `ApplyInProjectile follow_caster` | OK |
| Dash / blink / leap to target / charge | `MoveTo`, `DirTeleport`, `MoveToTarget`, `RushTime` | OK |
| Stun, knock-up, root, slow, silence, disarm, fear, charm, taunt, knockback, pull | `Stun`, `Airborne`, `Bind`, buff `move_speed_mult`, `BlockSkill`, `BlockAttack`, `Fear`, `Charm`, `Taunt`, `Knockback`, `Pull` | OK |
| Shield, heal, lifesteal, burn/poison | `Shield`, `Heal`, buff `vamp`, `AddCasted` | OK |
| Heal the ally who needs it (Soraka W) | `Targeting` + `AllyNotSelf`; the AI scores a heal by the target's missing health (champion-data "Which ally gets an ally skill") | ~ (AI choice) |
| Health cost (Soraka W) | `WithSelf` + `FixedAttack target_hp_ratio`, a short `undying` caster buff first | ~ |
| Global heal (Soraka R) | `Targeting AllyChampion` range 960000 + `RangeEffect` 960000 on `AllyChampion`; no bonus on low-health targets | ~ |
| Move faster toward low-health allies (Soraka passive) | no move direction or ally health in data: a move-speed caster buff after the ally heal | ~ |
| Passive stacks, every Nth attack | `SwitchByBuff` chain on hidden buffs | OK |
| Skill empowers next attack | ready-buff + `SwitchByBuff` in `attack` | OK |
| Mark on the target that the next attack detonates (Lux's Illumination) | `SwitchByBuff` only sees the caster's buffs and no effect removes a target's buff, so skill hits add a hidden caster ready-buff (the next attack on any enemy detonates it) and play a short mark `ViewEffect` on the hit target | ~ |
| Skillshot that stops after N targets (Lux Q: two) | `LinearProjectile` only has `penetrate` true/false; the mod SDK's `LinearProjectileEffect` has no hit-count field | ~ |
| Skillshot, then dash to the unit it hit (Lee Sin Q2, Blitz/Naut hooks) | `MoveToTarget` inside the projectile's `applied_effects` (LoL Reborn Nautilus Q); a `Delayed` there keeps the hit unit as target; no recast, it dashes by itself | ~ |
| Kick back + collision (Lee Sin R) | `Targeting`: `Attack` + `Knockback` on the target, plus a penetrating `LinearProjectile` toward it at the knockback's speed that knocks up what it passes (LoL Reborn Nautilus R) | ~ |
| Stacking bleed (Darius passive) | `AddCasted {casted_type: Bleed}` on every hit: each cast is its own instance, so the target's stacks are real (no cap) | OK |
| Bonus at N stacks on the target (Noxian Might; Darius R +20% per stack) | `SwitchByBuff` cannot read the target, so count the caster's own hits with hidden buffs and branch on those (champion-data "Bleed that stacks") | ~ |
| Cone pull to self (Darius E) | `RangeEffect` `Forward` + `DirDot` cone + `Grab` without `tick` (stops at the caster; `Pull` overshoots close targets) | OK |
| Bonus on a kill (Jinx's Get Excited!) | a kill check: an invisible champion-only twin of the projectile flags the caster, a short `AddCasted` on the target clears the flag while it lives (champion-data "Kill trigger"); the hero's own killing blows only, not assists | ~ |
| Reset / refresh on kill (Darius R, Katarina) | the kill can be detected (row above), but no effect resets a cooldown (`ult_cooldown_mult` untested) | X |
| Weapon swap the player chooses (Jinx Q) | automatic by distance: the long weapon's range on the attack, the short one while an enemy is close (champion-data "Weapon picked by distance") | ~ |
| Trap that lasts and springs once (Jinx E) | a chain of short links, each checking once; a bite locks the chain (champion-data "A trap that waits and snaps once") | ~ |
| Trap that waits long, several at once (Teemo R) | flat `Delayed` links of a `Position` cast, a trigger zone and a damage zone per trap, one set of flags per slot (champion-data "A trap that lasts, with three at once"); 12 s instead of minutes, gone when the caster dies | ~ |
| On-hit poison over time (Teemo E) | `AddCasted Poison` in the attack's projectile: every hit adds its own 4 s poison (League refreshes one), so the numbers count on the stack | ~ |
| Blind (Teemo Q) | `BlockAttack`: the target cannot basic attack; the game shows a disarm icon | OK |
| Invisible while standing still (Teemo's Guerrilla Warfare) | nothing reads stillness: `CasterInvisible` for 1.5 s with the move-speed skill, the attack-speed bonus beside it | ~ |
| Toggled aura (Amumu W) | on while fighting: every action starts a guarded train of `Delayed` pulses around the caster (champion-data "Aura that runs while he fights") | ~ |
| %-max-health magic damage (Amumu W) | `ApAttack` has no `target_hp_ratio`: the % part becomes `FixedAttack` (true), whole percents only | ~ |
| Amplify one damage type (Amumu's Curse: +10% of magic damage as true) | no per-type amplify field: `damaged_amplify` on all damage, re-applied so it never stacks | ~ |
| Hook that pulls the caster in (Amumu Q) | `LinearProjectile` on `EnemyChampion` + `MoveToTarget` in `applied_effects` | OK |
| Cooldown reduced when hit (Amumu E) | no "was hit" trigger: a shorter fixed cooldown | X |
| Charges (Amumu Q: 2, Teemo R: 3) | `cooltime_use_count: N`: N charges, each refilled in `cooltime / N`, one after the other (champion-data "Recast / charges", measured). league_amumu keeps 1 and a shorter cooldown (chosen before this was known); league_teemo R has 3 of 20 s, spent as targets come | OK |
| Ability treated as a basic attack (Yasuo Q: crits, on-hit) | the action's `attack_type: BaseAttack` (champion-data "Critical strikes") | OK |
| Crit chance up, crit damage down (Yasuo, Yone passive) | a flat `crit_chance` stat or buff; a crit is always 2x and the chance cannot be multiplied | ~ |
| Third cast changes (Yasuo Q3) | two hidden stack buffs + `SwitchByBuff` (champion-data "Third cast is different") | OK |
| Cast during a dash changes the shape (Yasuo EQ) | window buff from the dash, checked by the other skill | ~ (AI timing) |
| Dash through a target (Yasuo E, Fizz Q) | `RushMoveToBack`: lands 15000 units past the target, then its `applied_effects` | OK |
| Blocks projectiles (Yasuo W, Braum E, Samira W) | nothing can block a projectile. league_yasuo tried a picture of the wall + `base_attack_damaged_reduce` on allied champions around the caster; the user found it odd in this game and had it removed - leave such skills out | X |
| Only on airborne enemies (Yasuo R) | `EnemyChampionInCC`, which also counts stun, root, fear and charm | ~ |
| Shield when damaged (Yasuo Flow) | a hidden cooldown buff; the next action after it ends shields him | ~ |
| Skillshot that roots the first champion and pulls the caster to it (Leona E) | a penetrating damage `LinearProjectile` on `EnemyWithoutTower` plus a hidden non-penetrating twin on `EnemyChampion` whose `applied_effects` hold `Bind`, the root's view, `MoveToTarget` and `CasterAnimation` (the dash) | OK |
| Shield up now, burst later (Leona W) | `AddCasterBuff` damage reduction + a `Delayed` burst wrapped in `SwitchByBuff` on that buff (no burst after she dies); a hit re-adds the reduction once per cast behind a short lock buff | ~ |
| Allies' hits on a marked enemy deal more (Leona's Sunlight) | `damaged_amplify` 10% for 1.5 s on every enemy a spell hits: all damage, not an ally's next hit | ~ |
| Circle with a stronger centre (Leona R: slowed in it, stunned in the middle) | two `RangeProjectile`s on the same spot with the same `delay` / `apply`, radius 36000 and 16000 (champion-data "Telegraphed AoE") | OK |
| Stealth | `Invisible` / `CasterInvisible`: hidden from the enemy team's vision, but enemies next to the unit see and target it (champion-data section 4) | ~ |
| Untargetable blink strikes on the target and enemies near it (Master Yi Q) | invulnerable instead: `CasterInvisible` + a `damaged_reduce` 100 / `cc_immune` caster buff for the whole Q, `Teleport` + strike, then `Delayed` `RandomTarget` bounces; repeats on one target possible (champion-data "Invulnerable blink strikes"). A self-`Banish` between the strikes made the monsters and enemies around him vanish for his team | ~ |
| Channelled self-heal cast when hurt (Master Yi W) | the AI casts a heal on itself whenever it is ready, at any health (champion-data section 3): a short channel with damage reduction and a heal over time, cast as a fight starts, folded with a steroid (Wuju Style) | ~ |
| Immune to slows (Master Yi R) | no field: slows are buffs, `cc_immune` / `toughness` only touch CC; a big `move_speed_mult` offsets them | X |
| Takedowns refund cooldowns (Master Yi R) | no cooldown reset: `skill_cooldown_mult` (recharge speed) while the ult lasts | ~ |
| Every Nth spell stuns (Annie's Pyromania) | hidden caster buffs count casts (a folded spell counts twice); the cast decides it carries the stun, a hidden champion-only twin of its projectile or area stuns and uses it up a tick later, so minions never waste it (champion-data "Every fourth spell stuns") | OK |
| Spawns with a charge ready (Annie's Pyromania) | death clears a mod's buffs (champion-data section 5): a `Permanent` flag every action checks first fires once per life | OK |
| Shield that hurts attackers (Annie E) | `WithSelf {Shield}` + a `WithShield` buff with `damage_reflect` (a share of every hit, basic attacks and skills, not League's flat hit once per attacker) | ~ |
| Summon that fights (Tibbers) | cannot walk or attack in data: a `Position` cast lands his damage, a zone burns every second, his pictures (drop, standing loop, vanish) are `Delayed` `ViewEffect`s on the spot (champion-data "A summon that lands, stands and burns") | ~ |
| Refund on a kill (Annie Q) | detectable (kill trigger) and a short `skill_cooldown_mult` burst would speed the recharge, but it speeds every skill; league_annie leaves it out and keeps League's 4 s cooldown | X |
| 2-3 stage recast | `cooltime_use_count` or recast buff + `SwitchByBuff` | ~ (AI timing) |
| Cone / fan of projectiles (Ashe W) | no angle field on any projectile (base harpooner's fan is `Native`): a `LineRangeProjectile` rectangle cast by `Direction`, drawn as a fan sprite centred on it (champion-data "Cone / fan"); the hit area stays a rectangle | ~ |
| Untargetable / invulnerable | `Banish` on self (`WithSelf`; it also makes the unit invisible, puts a CC state on it, stops the caster's own `RandomTarget` finding units and takes away its team's vision around it - only for a caster leaving the fight); in a fight `CasterInvisible` + a `damaged_reduce` 100 / `cc_immune` buff: targetable, but every hit deals 1 | ~ |
| Execute / missing-HP scaling | `FixedAttack target_hp_ratio` (a share of *max* health; no effect reads missing health), flat bonus | ~ |
| Effect scaling with distance / charge time | fixed middle value | ~ |
| Summons, clones, turrets | zones/projectiles that deal the damage (LoL Reborn's Azir) | ~ |
| Transformation / stance | form buff + `SwitchByBuff` + long `CasterAnimation`; one sprite file per hero, so the "other form" must live as tags in the same `.aseprite` | ~ |
| Terrain / walls, global map mechanics, vision games | - | X |
| Resource bars (energy, rage, ammo) | stack buffs, or drop | ~ / X |
| Items, summoner spells, runes | - | X (ignore) |

If more than one core identity mechanic lands in the X column, choose another hero.

## Choosing the next hero (score 1-5 each, pick the highest total)

- **Recognition** - would a fan name the hero from a 35 px silhouette?
- **Kit fit** - share of the kit in the OK column above.
- **Sprite cost** - humanoid with one signature prop is cheap; mounts, huge creatures,
  transformations and summons cost 2-3x.
- **Roster gap** - fills a TFM2 category/role the pack lacks.
- **Showcase** - one signature VFX that sells the update GIF (a sun arrow, a sword storm).

## Numbers

Start from the base ranges in `champion-data.md` section 2 for the hero's category, then
translate relative strengths: if the source hero's skill is its main damage, give it the
larger ratio; long source cooldowns stay long relative to the hero's other skills. Ultimates
sit at 2400-3600 ticks. Never copy raw numbers from the source game.

Two corrections from players:
- A multi-hit skill needs its total, not League's per-hit number: league_garen E had League's
  per-spin 12 + 32% AD for 7 spins, less than auto-attacking for the same 3 s, and players
  thought it dealt no damage (now 25 + 55% a spin). Compare every damaging skill with the
  auto-attacks the caster gives up while casting it.
- When LoL Reborn already has the hero with the same effects, the user wants its numbers, not
  a weaker re-tune (players compare the two packs side by side): league_lux copies Reborn's
  stats, damage, ranges, cooldowns and hit areas. Where our kit is our own design (league_yasuo)
  it keeps its own numbers.

### Balance check: simulate on the SDK

`mod-sdk/deps` holds the compiled `game_core`; a small Rust program built against it with the
SDK's toolchain (`rustup run nightly-2026-05-24 rustc --edition 2021 -L dependency=<sdk>/deps
--extern game_core=... serde_json bincode bumpalo rand`) plays whole 5v5 games with the real AI:
`GameRunner::new(seed, false, Arc<GameSetting>, Arc<MapSetting>, Arc<ItemSetting>,
Arc<ChampionInfoSheet>)`, `set_macro_weights`, `add_player(GamePlayer::new(i, name, team,
Position, AthleteStat, id, Arc<dyn ChampionInfo>, vec![]))`, then `run_tick(&mut Bump, true)`
per tick. A mod hero is `ModChampionEntry::from_data_champion_info(&DataChampionInfo, None)`;
base heroes come from the sheet (`get_champion_info`). The settings come from the game's
asset bundle (game setting and item setting as JSON, the map setting as bincode). `Game` and
`DeathMatchGame` alone have no champion AI. Each frame's events carry every action with its
target (`EntityEvent` / `Action`) and `PlayerStatistics` (deal, tank, heal, self_heal, cs,
cs_jungle, kills, deaths, assists): the numbers players read after a match. Ten game minutes
take ~4 s, so average 12-16 seeds per lineup and change one thing at a time; the same lineup
varies about 10% between batches. The simulator and the extracted settings stay local.

## League of Legends specifics

How LoL Reborn (all 32 heroes, both authors) fits four abilities into three slots:
- `ult` is always R. `skill` / `skill2` are the two most iconic basics.
- The third basic and the passive are **folded in**, written as "Passive: ..." or as an extra
  effect of one of the two skills (Jax: E + passive stacks; Vi: Q + Blast Shield; Galio: E + W
  shield/taunt; Alistar: R + E heal). Silverbear's simpler heroes just drop them.
- Example (league_garen): Q Decisive Strike + W Courage (shield, damage reduction, tenacity) ->
  `skill`; E Judgment (`CasterAnimation spin` for 3 s, plus a short `MoveToTarget` in each of the
  7 damage pulses because the forced animation holds him still; cast as `Targeting` so the dashes
  have a target) -> `skill2`, with
  Perseverance as high `hp_regen` noted in its text; R Demacian Justice -> `ult` (true damage;
  missing-HP scaling exists only in base-only Native effects, so use `target_hp_ratio`).
- Ids: `<mod_id>_<champion>` (`league_garen`). The user's own `lol_mod` uses `lol_*`, so keep a
  different prefix for anything that may be installed next to it.
- Text: official names per language (zh-hans from the Chinese client, zh-hant, en, ko, ja).
- Assets come from the local client, read-only: `tools/lol/riot.py` reads WAD 3.x (xxh64 path
  hashes, zstd via Python 3.14 `compression.zstd`), Riot WPK packs and Wwise banks (bank version
  145: events -> actions -> sounds/containers), and resolves `Play_sfx_<Champ>_*` /
  `Play_vo_<Champ>_*` event names (plain strings in the champion `.bin` files) to .wem media;
  vgmstream decodes the .wem. Ability icons are `ASSETS/Characters/<Champ>/HUD/Icons2D/*.dds`.
- Chinese voice: `<Champ>.zh_CN.wad.client` in the Tencent (WeGame) client; inside it the banks
  keep the `vo/en_us/` path. A voice line whose media bytes are identical in the zh_CN and en_US
  banks is a wordless shout or a line left untranslated (Yasuo's R "Sorye ge ton"); comparing the two
  banks finds them without listening (`tools/lol/extract_yasuo.py`). A `.sound_info` always plays the
  same clips (no random pick), so choose one variant per sound.
- Real animations as pose references: `tools/lol/pose_ref.py --anim Run --frames 6` skins the
  champion's `.skn`/`.skl` with an `.anm` clip (compressed `r3d2canm`, or uncompressed
  `r3d2anmd` v3 / v4 / v5 - most of Lux's clips are v3, her R is v4) and renders textured
  3/4-view frames. The diffuse texture is `*_TX_CM` (Garen, Ashe) or `*_CM_TX` (Lux); without
  one the model renders grey. Clip names come from
  `data/characters/<champ>/animations/skin0.bin` (Garen: `Idle1`, `Run`, `Run_Spell1`,
  `Attack_01/02`, `Crit`, `spell1/3/4`, `Death`). Attack clips are ~2 s with the swing in the
  first ~0.4 s - pick frame times with `--times`. Use `--mirror` when the pose turns the chest
  toward the champion's right (Garen's idle and Attack_01): it renders the other side and flips
  it, so the sprite still faces right with its front showing.
- **Which clip plays when.** The animation bin maps clip names to files as `FNV-1a(lowercase
  name) -> AtomicClipData { path }`; hash candidate names (`Run`, `Run2`, `Spell4`...) and read the
  path that follows. Ashe: `Run` = `ashe_run_walk`, `Run2` = `ashe_run_jog`, `Run3` = `ashe_run`;
  `Spell4` (R) reuses `ashe_crit1`; Q is `Ashe_spell1_IN` then `ashe_spell1`. Newer champions
  route through logic clips: after the key hash comes the class hash (`FNV-1a` of
  `AtomicClipData`, `SequencerClipData`, `ConditionBoolClipData`, `ConditionFloatClipData`,
  `SelectorClipData`), and the non-atomic ones list other clip hashes. Lee Sin: `Idle1` = sequence
  `Idle_Active` (combat stance) then `Idle_Passive`; `Run` = `Run_Homeguard` or, by speed,
  `Run_Base.anm` (its haste branch plays the same file); `Crit` = `Attack4`; Q2 = `Spell1_B` then
  `Spell1_B_Loop`. TFM2 heroes are always fighting, so take the combat idle. Older champions have
  only atomic clips (Soraka: `Idle1`, a single `Run`, `Attack1/2`, `Spell1`-`Spell4`, `Death`),
  so there is no combat-run branch to look for.
- **Walk or run: measure it.** During stance a planted foot slides back at the clip's ground
  speed; compare it with the champion's movement speed, and look for frames where both feet are
  off the ground (a run) or one foot always down (a walk). Ashe's jog/run clips move ~305 units/s
  (her base move speed is 325) with a flight phase, so she runs; the walk (~250) is her slowed
  gait. Time the TFM2 loop from the clip's own cycle (Ashe: 1.0 s, 8 x 125 ms). Lux has a single
  `lux_run` (a 4.8 s file holding six 0.8 s cycles): both feet are off the ground for about half
  of each cycle, so she runs (8 x 100 ms). Lee Sin's `Run_Base` is a leaping run: 1.53 s for two
  strides, each with ~0.4 s in the air (8 x 192 ms).
- **Render side, per champion.** Some champions show their chest from one side, some from the
  other (Garen and Lux need `--mirror`, Ashe does not) - render idle both ways and look for the face.
  Then use that same side for *every* clip of the hero: the renders appear to be mirror images of
  the game (Ashe's bow hangs off her `R_hand` joint but shows in her left hand), so switching
  sides between clips moves a one-handed prop to the other hand. TFM2 flips sprites that face
  left anyway, so the handedness itself does not matter.
- **Start and end near idle.** League cross-fades clips (about 0.2 s), and many clips start
  mid-action (Ashe's attack opens at full draw). `pose_ref.py --frame "idle@0>attack@0:0.5"`
  renders that blend, so each strip can open and close half-way to idle instead of popping.
  `--hq` textures per pixel (face and trim readable) - better pose references and a design sheet
  (three `--yaw` views of the idle frame).
- **Render them chibi.** League's adult proportions pull the image model to a small head even
  when the prompt says "chibi": Garen and Ashe came out with heads 1/5 of their height (base
  heroes: 1/3), so in-game their faces were two or three rows of skin without eyes.
  `--head 2.0 --legs 0.8` scales the head joint and every leg, cape, skirt and cloth chain and
  keeps the legs' lowest point where League has it (landings and jump heights unchanged) - the
  references then show the proportions to draw (`assets/source/CHIBI_REDRAW.md`). Use it from the
  first prompt of every new hero; the redraw of both heroes came back right in one round.
  Everything below the head joint grows with it: Lee Sin's long braid (`Hair1`..`Hair12` under
  `Head`) reached the ground at 2x. `--hair 0.5` scales the hair chains back to League's length.
  Check where the hair hangs from: Soraka's ponytail chain starts at `Chest`, so it keeps League's
  length by itself. Her horn has a `horn` joint under `Head` but no skin weights of its own - it
  rides on the head and doubled with it, its tip becoming the crown. `--keep horn:4`
  (`"keep": {"horn": 4.0}` in `chibi` of a native_pose spec) binds the head vertices above that
  joint and within 4 units of it to the joint, so `--hair` holds the horn at League's size and the
  crown is measured without it (`pose_ref.keep_parts`).
  **Measure the head share before scaling it.** Some champions are chibi already: Amumu's head is
  63% of his height at `--head 1.0` (the head part of a `native_pose.py --parts` render, rows of
  the design pose), 91% at 2.0 / 0.8 and 53% at 0.8 - so league_amumu keeps League's proportions
  and the user picks from a side-by-side sheet against base heroes. Base TFM2 heads are about 36%;
  the base ghost and ogre show that big-headed creatures fit the style.
- **Texture and side for a drooping head.** The diffuse texture is found by name (`*_TX_CM`,
  `*_CM_TX`) or, failing that, as the base skin's texture that is not a load screen or icon
  (`pose_ref.diffuse_textures`; Amumu's is `SadMummy.tex`). Amumu's idle hangs his head to the
  right, so at yaw 55 only the near eye shows; yaw 40 shows both (look at `--hq` renders at 0/30/55
  before picking). His `Spell2` clip, 0.34 s, is the flat flying pose of Bandage Toss's pull and
  serves as the `q_pull` tag.
- **Game size straight from League (Lee Sin: worked, one GPT round).** The native-size
  redraw needed a first GPT round only to turn League's poses into game frames.
  `tools/lol/native_pose.py <hero>/poses.json` renders the clips at game size instead: the chibi
  model through one camera, the design pose `height` px from crown to soles (hair chains not
  counted), each game pixel the mean colour of an 8x8 block of an `--hq` render, in the native
  grid, next to the same frames as the 8x render, plus `<hero>_cells.json` for
  `tools/art/import_native.py`. Per tag: `lunge` (share of League's travel kept, 0.7 for
  actions), `anchor: first` (Lee Sin's death starts 140 units in front of the unit), `flat`
  (each frame's lowest point as high above the feet line as above League's floor - a body lying
  diagonally in depth otherwise floats or sinks through the pitch); per frame `turn` degrees
  toward the camera for spins and bent-over slams that would show the back, and `head_like`
  (per tag or per frame) to turn the head the way it faces in another pose, the body untouched:
  a chibi head bowed toward the ground shows only its crown (Soraka's Q and R bows keep her face
  with `"head_like": "Soraka_Idle1@0"`), and `rise` (per tag) to keep only that share of League's
  height while the whole body is off the ground (Darius's Noxian Guillotine leaps five metres:
  0.18). When `turn` cannot bring the chest round (Darius's Q spin faces straight away at 100 ms,
  his W sweep twice), pick the neighbouring times that face the camera instead. Cells can be bigger
  than 56x64 (`"cell": [64, 72]` for the braid and the flying kick), and a third value moves the
  feet line up from its 10 px (`[88, 96, 18]`: Darius's axe lands 16 px below his soles, the pitch
  drawing the ground in front of him lower on screen). The feet line holds the design pose's lowest
  point; the pivot sits 11.5 px above the soles, found in a render of the legs alone (until
  2026-09-27 it was counted from the lowest point, and Darius, whose axe hangs 5 px below his
  soles, floated 5 px in game). The cells table also records League's head joint per frame. GPT followed the poses but drew every action except idle about
  1.4x the design (heads more than bodies) and its jumps too low; `tools/art/fit_native.py`
  shrinks each strip back by the head (a 16-colour vote, still flat pixels) and puts each frame's
  blindfold on League's head joint, soles back on the line where the reference stands - check
  every strip's head against idle before importing. Soraka's delivery went the other way: Codex
  pasted the approved design's head into every frame (no size drift, steady loops), so a flaw in that
  head showed in all 52 frames at once; one template swap fixed them all (find the pasted head exactly
  in each cut frame, recolour the changed pixels through `<hero>_retouch.json` - `soraka_retouch.json`
  adds a fringe and a side lock). `import_native.py` starts its idle head search at the top row, which
  for Soraka is her staff's crescent, so the other strips report no head column - harmless when the
  delivery already keeps it steady.
- **Straight from League, recoloured (Darius: worked, no GPT strips).** Codex assembled Darius's
  strips from blocks on the grid: the body changed size between frames, the cape was a red slab, the
  run held the axe as a pole. When a delivery's bodies are built rather than drawn, take the pixels
  from League as well: `native_pose.py --alpha --parts` renders every tag on a transparent background
  with a part map (head red, weapon green, body blue; the spec's chibi `scale` enlarges named
  joints - his pauldrons 1.4x, as big as the design draws them), and `tools/art/restyle_native.py`
  votes each 8x8 block into the design sheet's palette (the weapon by brightness, the body by hue:
  crimson, skin, steel with a bright trim), draws the outline outside the silhouette so thin limbs
  keep their colour, lifts the frame a pixel so the outline under the soles lies on the sole row, and
  pastes the design's head on League's head joint (a quarter turn when he lies on his back, from the
  cells' `tilt`; a bowed head stays upright). Result: 18 colours, 37% right-neighbour, League's
  motion, lunges and jumps, and one model in every frame, so the body never changes size. The body
  comes out slimmer than a hand-drawn design; enlarge what the design exaggerates, and keep the
  effects from the delivery.
  Amumu (2026-09-27) went this way end to end. Codex's image tool could not hold the grid even for
  the design sheet (raw 1254 px output, ~13.45 px blocks, 29 blocks tall), so the design was drawn
  square by square on League's own 34 px silhouette of the design pose (parts outlined one by one,
  the style taken from Codex's draft) - it then lines up with the pose references and the restyle.
  The strips came back as raw generations too (soft alpha, other canvas sizes, a new head in every
  frame, standing heights 32-47 once converted), and the user picked the restyle from a
  side-by-side GIF. An all-bandage hero gives every ramp of `restyle` the same five greens (cuts
  from the design's own tone shares). `"turn": {"dead": 50, "*": 180}` turns the pasted head only
  in the death strip: a head thrown back in a jump (tilt -50 to -65) turned a quarter read as a
  barrel with vertical stripes. Raw effect strips become native strips with
  `tools/art/import_amumu.py --raw` (median-cut colours, majority per game pixel, a scale per
  effect set by the kit's radius).
- **Raw effect strips whose frames are not evenly spaced (Jinx, Codex effects only).** Six equal
  cells cut the rocket blast mid-fireball: `tools/art/import_jinx.py --raw` cuts each strip at the
  n - 1 widest empty column runs (strips whose own drawings have wide gaps - three smoke puffs, a
  ring of sparkles - get their cut columns written out) and places every frame in its cell on an
  anchor: projectiles on their nose (no jitter, the nose meets the target), traps and bites on the
  ground line the strip was drawn on, a ring on the rows without the speed streaks. Effects that
  play one after another must match: Codex drew the arm / wait / fizzle rows of chompers at 589, 635
  and 504 px, so each strip gets its own scale to the kit's width, and the five chomper strips share
  one palette (per-strip median cuts turned the arming flames pink and the waiting ones orange). A
  rocket's body wobbles between generated frames: keep frame 1's body in every frame, only the flame
  moving. Place projectiles at the caster in the showcase: a 59 px rocket starts over her body.
- **A ponytail that swings, a palette beyond crimson, a head that turns (Yasuo, drawn by Claude,
  restyled).** Codex's image tool missed the grid again (1254 px canvas, blocks 9.6-10.8 px), so the
  design was drawn on League's 34 px silhouette like Amumu's: every render pixel votes for a colour
  by part and material, then the face, the sheath's edge, the pauldron's grooves, the rope belt and
  the chest were drawn square by square - 19 colours. The strips come from `restyle_native.py` with
  these additions (Darius's and Amumu's strips stay byte for byte without the keys):
  - `"materials"` (hue / saturation / value windows, first match wins) replace crimson / skin /
    steel. League's lighting is dark: Yasuo's chest sits at value 0.27 and the rope in shadow at
    0.13-0.36, so skin starts at 0.1 and gold is any saturated pixel of hue 32-55 whatever its value
    (skin and leather sit at 16-31); darker, both came out as a brown vest.
  - `native_pose.py` `"hair_part": true` paints the hair chains (pose_ref HAIR: Hair1-4, Hair_Top)
    yellow, so the ponytail is voted frame by frame instead of riding on a pasted head.
  - The head. Pasting the design's head (Darius, Amumu) made a sticker: upright while League's head
    bowed in the run, turned away in the EQ spin and lay down in death, and the user saw a head apart
    from the body. `"head": {"mode": "voted"}` votes League's head too (gold tie, skin, hair), flattens
    the face into the design's two tones (a dark jaw of League's stubble read as a mask) and pastes
    the design's whole face block (forehead, brows, eyes, cheeks, mouth: 6x6) on the face this frame
    shows: the far eye on the face's front edge in the eye row, mirrored when it looks left, left out
    when it turns away (`native_pose.py` `"face_track"` writes each frame's face point, facing and
    side from the head joint's up / forward axes). Pasting only the brow and eye squares let the
    fringe swallow the brows and the mouth land on the cheek - the user found eyes and mouth strange.
    The frames no rule fits (bowed: downcast eye lines; profile: brow, eye, mouth on the front edge;
    lying: closed eyes; a tie that flickered) are retouched by hand in `yasuo_retouch.json` (14
    frames, 35 squares). Check every frame's face at 12x before sending a GIF.
  - Shrinking a hero: the user found Yasuo a size bigger than the others and chose, of three
    options (all 80%, body 80% with the head kept, all 88%), the body at 80% with the head kept
    (`"height"` 30, `"chibi"` head 2.4 and hair 0.417: the head's pixel size unchanged). The same
    face block on that head read as a horse face with its right side cut flat, a crooked mouth, and
    a far eye that merged with the hair into one dark line (one-eyed, the user said). What fixed it,
    in the block and three `"features"` keys: the fringe covers the forehead but for two squares;
    the chin's front corner steps in with an outline under the chin; `"neck"` recolours body skin
    within two squares of the face, below the eye row, to the scarf (the neck under the chin made
    the face a row longer); the far eye was redrawn with a white and the mouth in red between the eyes,
    but the user then found the face cute, "not a samurai at all", and wanted the pre-shrink
    features back: the final face keeps them (forehead, slanted brow, a narrow eye with one white,
    the far eye a dark slit, a small dark-brown mouth, jaw shadow) over the short round chin. Fix a
    face's shape without changing its expression. `"trim_front": 4` cuts a one-square bump of League's fringe past the face's front
    edge above the eyes and redraws the outline (not when hair covers the face in the eye row: cut
    there, ult 7 got a notch); `"hair_above": 2` turns the forehead skin above the drawn fringe
    into hair. `"skip"` leaves pixels of the `"rect"` out, and `"pixels"` entries may carry a colour
    (`[x, y, least facing, "hex"]`). Show the user the face at 12x next to the base heroes' faces
    before redrawing all frames: base chibi faces have no mouth and a 2 x 2 near eye, 1 x 2 far eye.
  - The run (0.10.0): League's run bows his head until the face turns into profile (facing 0.25-0.36,
    under the mouth's 0.45), and the block's lower rows landed differently in each frame - the chin
    line over skin read as an open mouth in some frames and not in others (the user: a mouth that
    comes and goes). `"head_like": "Yasuo_Idle1@0"` on the run keeps the idle's head: the same face
    in all eight frames, mouth included; the one skin square left under the chin in run 1 goes to
    the scarf (`yasuo_retouch.json`). Check a run's faces for a steady mouth, not just its eyes.
  - `"hide"` per tag: the drawn sword has no track in the death clip and stood upright beside the
    body. `"chibi": {"scale": {"L_Rope_Back1": 0.6, ...}}` shortens the rope tails that flew out as a
    big gold fan in the run.
  What Yasuo holds at his hip in idle is the sheath (League's weapon part there is only the hilt);
  the drawn blade appears in attacks next to it. `import_native.py` steadies idle and run on
  League's head joint for a voted head.
- **A shield, a crown and a face under thick hair (Leona, drawn by Claude, restyled).** The spec's
  top-level `"parts"` paints her shield (a mesh on its own root joint) and her cloth in part colours of
  their own in `--parts` renders; `restyle_native.py` votes each by its own materials and, with
  `"outline": true`, outlines what touches the shield, which otherwise came out as one gold mass with
  her armour. `"crown": 165` measures the chibi crown from the hair (the spikes stand 12 units above
  it and, counted as the crown, shrank everything else). Next to the base knight she stood 29 px
  hair to soles, so `"height"` went to 39 (33 px hair to soles, 42 with the crown). Her small face
  gave too little voted skin to place the block: `"features"` `"profile"` (a facing below which only
  the block's front four columns go on), `"chin"` (rows that far below the eyes may paint over the
  collar) and `"fallback": "track"` (the tracked point is the far eye where too little skin is voted).
  The run bowed her head behind the shield: `"head_like"` keeps the idle's head (Yasuo's run got the
  same fix later). Idle is one drawing (`ORDER`) with a breath (`BOB`) down to the shield's tip. Her
  ten effects came from Codex as raw generations like Jinx's: `tools/art/import_leona.py --raw`
  reuses `import_jinx.split` (the Eclipse burst's flaming rings nearly touch: its cut columns are
  written out), scales each effect to the kit (burst ring 70 px, flare ring 72 px, both drawn at half
  and enlarged 2x), anchors rings on the ground row Codex drew them on, moves the shield bash's star
  frames from the chest to the head, and lists the stun stars twice to cover the 1.75 s stun. Keep
  overhead marks and stun stars apart - the Sunlight mark 30 px above the pivot, the stars on a 34 px
  head's top (16 px) - or they merge into one clump.
- **A head bigger than the body (Teemo, drawn by Claude, restyled).** A yordle is chibi already: League's
  own proportions give Teemo a head (hat and ears) of 56% of his height, so `chibi` stays 1.0 and only his
  feather (0.6) and backpack (0.7; full size it read as a pair of wings) shrink; `"crown": 115` measures
  34 px from the hat's top, the feather standing above it. His skin has three colour maps (body,
  harmonica, mushroom) and the harmonica's sorted first, turning the whole model brass:
  `pose_ref.diffuse_textures` now takes the map the skin bin names right after the mesh (every earlier
  hero keeps its map), and `"hide_submeshes": true` leaves out the submeshes the skin hides until a clip
  shows them (his mushroom and harmonica; the bin's initialSubmeshToHide). A voted head (Yasuo, Leona)
  came out as red goggles over broken bits of green hat; with the head the biggest part of him, it was
  drawn once, square by square, and is pasted on League's head joint (Darius, Amumu) while the voted body
  keeps League's motion. The block starts left of and above League's head part (its outline and the far
  ear), so the spec gives `"dx"` beside `"dy"`; for lying frames, turned a quarter, the two are folded into
  the joint's place before the turn, or the head lands beside the neck (the user saw it come off his body
  in death). His death throws him 320 units back, out of the render: a tag's `"travel"` keeps that share of
  the root's way across the floor (0.3). Frames where League flips him (R's backflip, the death's tumble)
  are left out: a pasted head is upright or a quarter turned, nothing between. The same holds for
  a lean: League's run throws him forward (spine and neck bent toward the ground, legs kicked back so
  the feet float 1-8 px at the camera's pitch), and under the upright pasted head the user saw a head
  that did not grow out of the body. The run is now 60% League's run and 40% the idle
  (`Run@t>Idle@0:0.4`, picked from a side-by-side of 0, 40 and 60%) with `"flat": true`, the feet back
  on the ground; a pasted head wants a body that stays roughly upright under it.
- **A helmet instead of a face (Master Yi, drawn by Claude, restyled, head pasted).** League's 2013
  Yi hides his face under a helmet with a cluster of six green lenses. Voted like Leona's head, its thin
  gold trim and silver came out as a speckled blob that changed every frame, so the helmet was drawn
  square by square after an `--hq` render of the design pose (a 24x crop under a game-pixel grid), in
  the tilt League gives it in idle, and pasted into every frame (`restyle_native.py` paste mode: the
  rect's body pixels listed in `cut`; `dy -3`, one row for the frame's lift and two because the drawn
  crest starts above League's head box). League's head stays within 20 degrees of that tilt in almost
  every frame; in death he falls on his face, turned by `"forward": true` (unlike Teemo's quarter turn
  onto his back, the `dy` stays on the screen: his death frames were checked that way). The user saw three faces
  (the lens cluster, two lenses like eyes on goggles, goggles over an open chin with a dark-red mouth)
  and took the lens cluster, then had the gold chin guard cut to a small beak at its front: a gold bar
  under the lenses read as a yellow mouth. Camera yaw 40 unmirrored (the attack lunges right), head 1.8
  (38% of his height; 2.0 gave 41%, base heroes 36%), hair 1.0 (his `Hair1-4` chain is the helmet's
  gold crest), the short swords on his legs hidden. Idle is one frame breathing (`ORDER`, `BOB` seam
  just under the pivot: his back foot stands 5 rows above the front one, and a lower seam moved it);
  the run is steadied on League's head joint (`PASTED` in `import_native.py`: the raised sword is the
  top of every frame and crosses the helmet). 46 frames, 22 colours, 38% right-neighbour. His nine
  effects came from Codex as raw generations, like Leona's: `tools/art/import_masteryi.py --raw` cuts
  Alpha Strike's strip into equal cells (its burst touches the frame after it, so no empty column parts
  them), anchors the looping auras (Wuju, Highlander) on their equal cell's centre so they do not jitter,
  and scales the effects drawn round an empty figure (the Wuju wisps, the meditation, the Highlander
  burst) so that figure is his height.
- **A child with her teddy (Annie, drawn by Claude, restyled, head pasted).** League's proportions give
  Annie a head of 29% of her height (the head part of a `--parts` render of the design pose); the user
  picked 1.3 (35%) from 1.0 / 1.3 / 1.5 shown at game size next to base heroes. Her skin has one mesh and
  one colour map, nothing hidden. Camera yaw 35, mirrored: the face, the pinafore and the teddy in her
  near hand. The head (cat-ear headband with pointed ears, magenta bob with a fringe, green eyes built like
  base heroes' - lashes, highlight + pupil, white + iris, the far eye one square) was drawn square by
  square and pasted (`dx 1, dy -2`: the ears start a row above League's head box, plus the frame's lift);
  of three faces the user took B, with a one-square dark-red mouth. The teddy is the weapon part
  (`"weapon": "^R_Teddy$"`, a root joint of its own): voted on a brown ramp by brightness and outlined
  apart from her. A frame's `"hide"` (native_pose) removes it once it leaves her hand - held up to become
  Tibbers from the fourth ult frame on, thrown away as she dies - a bear flying off across the cell or
  held over her face read as clutter at game size. Attack and Q frames are turned 40-60 degrees toward
  the camera (League shows her back and backpack as she throws); the death skips League's 1.5 s of
  standing with her back turned and falls straight after the throw, the head turned by `"forward"`. Idle
  is one drawing breathing down to the shins; the run is 60% League's hopping run, 40% idle, `"flat"`.
  47 frames, 30 colours, 37% right-neighbour. Tibbers himself is an effect drawn by Codex from renders of
  his own model: a summon is a character of its own in its champion's WAD (`pose_ref.py --champ
  AnnieTibbers --wad Annie`, with his spawn, idle, claw swipes and death). Codex drew the bear at three
  sizes in his three strips (landing, standing, vanishing: 235, 218 and about 270 source px), so
  `tools/art/import_annie.py --raw` scales each to 42 px from his ears to his feet and gives the three one
  shared palette (per-strip median cuts would tint his fur differently in each); it reads the delivery's
  `assets[].frames[].rect` manifest, and squeezes Incinerate's cone, drawn wider than 50 degrees, into the
  kit's 56 x 50 rectangle with its point on the cell's left edge.
- **A face point under the hair.** `tfm2_ase.py face` and the lint find the crown at the top of
  the idle sprite, which for Yasuo is the ponytail's tip, 9 px above his head and to the left of
  it. Both now also look for the head from the face: the top two rows of skin-toned pixels and the
  silhouette above them. A face point on that head passes (an INFO line); one above the head still
  warns.
- **Clips that are not what their name says (Yasuo).** Read which animation a spell plays in
  `data/characters/<champ>/<champ>.bin`: the spell name is followed by its animation name (Yasuo:
  `YasuoQ1` -> `Spell1A`, `YasuoQ2` -> `Spell1B`, `YasuoQ3` -> `Spell1C`, `YasuoDashWrapper` ->
  `Spell3`, `YasuoRKnockUpCombo` -> `Spell4`). `Yasuo_Spell1_Wind.anm` (an uncompressed v4 file)
  animates only the hair and cloth - the Q3-ready overlay - and every other joint has a zero
  translation, so rendered alone it collapses into a heap; the whirlwind's body motion is `Spell1C`.
  A prop the clips leave without a track hangs at full size wherever its joint sits: Yasuo's flute is
  scaled to nothing in idle but floats beside him in his attack and death clips, so the spec leaves
  it out (`"hide": ["^flute$"]`). His katana hangs from a joint named `Sword`, not `Weapon`
  (`"weapon": "^sword$"` for `--parts`). His diffuse texture is `Yasuo_base_TX_CM`; the weapon
  trail's `Yasuo_Weapon_Trail_TX_CM` sorts first and was picked before `pose_ref.diffuse_textures`
  skipped trails (white model with holes).
  A deep stance is still measured from the crown to the soles: Yasuo's idle crouch is 80% of his
  standing height, yet base heroes in stances (the ninja) and this pack's Lee Sin are 34 px the same
  way, so league_yasuo is too; his wider silhouette comes from the stance.
- **Head tracks for the importer.** `pose_ref.py --frame <clip@ms> ... --track <hero px>
  --track-ref <idle clip@0>` prints each frame's head joint x in game px from the unit, for a
  hero that many px tall in idle, through the same camera and `--mirror` / `--head` / `--legs` as
  the references (the importers place each frame's drawn head there). The chibi skeleton moves the
  head 3-4% less than the adult one; Garen's hand-measured tracks had been 0.69x too small.
- **Official names** live in `Game/DATA/FINAL/Localized/Global.<locale>.wad.client` ->
  `data/menu/en_us/lol.stringtable` (RST v5: 38-bit xxh64 key hashes; the Chinese WADs keep the
  `en_us` path, like their voice banks). Find a string by its English text and read the same key
  in the other locale. The Tencent client has zh_CN, the Riot client here zh_MY (whose names
  differ in places: Ashe's Q is 射手的专注 in zh_CN, 专注射击 in zh_MY). For locales not
  installed, read Riot's public Data Dragon
  (`ddragon.leagueoflegends.com/cdn/<version>/data/<ja_JP|ko_KR|zh_TW>/champion/<Champ>.json`):
  Lee Sin's Japanese names (練気, 響掌/共鳴撃, 破風/縛脚) were nothing like a guess.
- Riot allows non-commercial fan content; keep extracted audio out of public repos anyway
  (re-extract with the tool) and add the disclaimer (League of Legends (c) Riot Games).
