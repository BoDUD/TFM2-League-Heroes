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
| Reset / refresh on kill (Darius R, Katarina) | no kill trigger in the effect tree | X |
| Toggled aura (Amumu W) | on while fighting: every action starts a guarded train of `Delayed` pulses around the caster (champion-data "Aura that runs while he fights") | ~ |
| %-max-health magic damage (Amumu W) | `ApAttack` has no `target_hp_ratio`: the % part becomes `FixedAttack` (true), whole percents only | ~ |
| Amplify one damage type (Amumu's Curse: +10% of magic damage as true) | no per-type amplify field: `damaged_amplify` on all damage, re-applied so it never stacks | ~ |
| Hook that pulls the caster in (Amumu Q) | `LinearProjectile` on `EnemyChampion` + `MoveToTarget` in `applied_effects` | OK |
| Cooldown reduced when hit (Amumu E) | no "was hit" trigger: a shorter fixed cooldown | X |
| Charges (Amumu Q: 2) | `cooltime_use_count` is "up to N times in succession" (base Nightmare's text); the AI would throw both at once *(inferred)*, so league_amumu keeps 1 and a shorter cooldown | ~ |
| Ability treated as a basic attack (Yasuo Q: crits, on-hit) | the action's `attack_type: BaseAttack` (champion-data "Critical strikes") | OK |
| Crit chance up, crit damage down (Yasuo, Yone passive) | a flat `crit_chance` stat or buff; a crit is always 2x and the chance cannot be multiplied | ~ |
| Third cast changes (Yasuo Q3) | two hidden stack buffs + `SwitchByBuff` (champion-data "Third cast is different") | OK |
| Cast during a dash changes the shape (Yasuo EQ) | window buff from the dash, checked by the other skill | ~ (AI timing) |
| Dash through a target (Yasuo E, Fizz Q) | `RushMoveToBack`: lands 15000 units past the target, then its `applied_effects` | OK |
| Blocks projectiles (Yasuo W, Braum E, Samira W) | nothing can block a projectile: a view-only wall + `base_attack_damaged_reduce` on allied champions around the caster | X / ~ |
| Only on airborne enemies (Yasuo R) | `EnemyChampionInCC`, which also counts stun, root, fear and charm | ~ |
| Shield when damaged (Yasuo Flow) | a hidden cooldown buff; the next action after it ends shields him | ~ |
| Stealth | `Invisible` / `CasterInvisible` | OK |
| 2-3 stage recast | `cooltime_use_count` or recast buff + `SwitchByBuff` | ~ (AI timing) |
| Cone / fan of projectiles (Ashe W) | no angle field on any projectile (base harpooner's fan is `Native`): a `LineRangeProjectile` rectangle cast by `Direction`, drawn as a fan sprite centred on it (champion-data "Cone / fan"); the hit area stays a rectangle | ~ |
| Untargetable / invulnerable | `Invisible` on self + `cc_immune` / `damaged_reduce` buff | ~ |
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
- **A ponytail that swings, a palette beyond crimson (Yasuo, drawn by Claude, restyled).** Codex's
  image tool missed the grid again (1254 px canvas, blocks 9.6-10.8 px), so the design was drawn on
  League's 34 px silhouette like Amumu's: every render pixel votes for a colour by part and material
  (the materials below), then the face, the sheath's edge, the pauldron's grooves, the rope belt and
  the chest were drawn square by square - 19 colours. The strips come from `restyle_native.py`, with
  three additions: `native_pose.py` `"hair_part": true` paints the hair chains (pose_ref HAIR:
  Hair1-4, Hair_Top) yellow, so the ponytail is voted frame by frame on a `"hair"` ramp while the
  design's head (without the ponytail) is pasted over the head; `"materials"` (hue / saturation /
  value windows, first match wins) replace crimson / skin / steel - League's lighting leaves Yasuo's
  chest at value 0.27 and the rope in shadow at 0.13-0.36, so skin starts at 0.22 and gold is any
  saturated pixel of hue 32-55 whatever its value (skin and leather sit at 16-31); `"head": {"dy":
  -1}` pastes the head a row higher, because the frame is lifted a pixel for the outline under the
  soles while the paste used League's unlifted head. Darius's and Amumu's strips stay byte for
  byte without these keys. `import_native.py` steadies idle and run on the pasted head for a
  `hair_part` hero (its top rows are the ponytail, different every frame). What Yasuo holds at his
  hip in idle is the sheath (League's weapon part there is only the hilt); the drawn blade appears
  in attacks next to it.
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
