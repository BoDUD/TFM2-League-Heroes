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
| Health cost (Soraka W) | `FixedAttack target_hp_ratio` in a `RangeEffect` on `AllyOnlySelf` (a `WithSelf` also hits the healed ally, champion-data section 4), a short `undying` caster buff first | ~ |
| Global heal (Soraka R) | `Targeting AllyChampion` range 960000 + `RangeEffect` 960000 on `AllyChampion`; no bonus on low-health targets | ~ |
| Move faster toward low-health allies (Soraka passive) | no move direction or ally health in data: a move-speed caster buff after the ally heal | ~ |
| Passive stacks, every Nth attack | `SwitchByBuff` chain on hidden buffs | OK |
| Skill empowers next attack | ready-buff + `SwitchByBuff` in `attack` | OK |
| Mark on the target that the next attack detonates (Lux's Illumination) | `SwitchByBuff` only sees the caster's buffs and no effect removes a target's buff, so skill hits add a hidden caster ready-buff (the next attack on any enemy detonates it) and play a short mark `ViewEffect` on the hit target | ~ |
| Skillshot that stops after N targets (Lux Q: two) | `LinearProjectile` only has `penetrate` true/false; the mod SDK's `LinearProjectileEffect` has no hit-count field | ~ |
| Skillshot, then dash to the unit it hit (Lee Sin Q2, Blitz/Naut hooks) | `MoveToTarget` inside the projectile's `applied_effects` (LoL Reborn Nautilus Q); a `Delayed` there keeps the hit unit as target; no recast, it dashes by itself | ~ |
| Kick into the ones behind, or get behind and kick back (Lee Sin R) | `Targeting`: `Attack` + `Knockback` on the target, plus a penetrating `LinearProjectile` toward it that knocks up what it passes (LoL Reborn Nautilus R); a hidden probe toward the target counts the champions on the line on the cast tick: someone behind it -> `MoveToTarget` to its front and the kick sends it into them; nobody -> `RushMoveToBack` and the kick from behind sends it back toward his side (champion-data "Pick the kick") | ~ |
| Stacking bleed (Darius passive) | `AddCasted {casted_type: Bleed}` on every hit: each cast is its own instance, so the target's stacks are real (no cap) | OK |
| Bonus at N stacks on the target (Noxian Might; Darius R +20% per stack) | `SwitchByBuff` cannot read the target, so count the caster's own hits with hidden buffs and branch on those (champion-data "Bleed that stacks") | ~ |
| Cone pull to self (Darius E) | `RangeEffect` `Forward` + `DirDot` cone + `Grab` without `tick` (stops at the caster; `Pull` overshoots close targets) | OK |
| Bonus on a kill (Jinx's Get Excited!) | a kill check: an invisible champion-only twin of the projectile flags the caster, a short `AddCasted` on the target clears the flag while it lives (champion-data "Kill trigger"); the hero's own killing blows only, not assists | ~ |
| Reset / refresh on kill (Darius R, Katarina) | the kill can be detected (row above), but no effect resets a cooldown (`ult_cooldown_mult` untested) | X |
| Weapon swap the player chooses (Jinx Q) | automatic by distance: the long weapon's range on the attack, the short one while an enemy is close (champion-data "Weapon picked by distance") | ~ |
| Trap that lasts and springs once (Jinx E) | short links as `Delayed` effects of the `Position` cast (they stop when the caster dies), each checking once; a bite spends the trap, per-trap slots and a heartbeat (champion-data "A trap that waits and snaps once") | ~ |
| Trap that waits long, several at once (Teemo R) | flat `Delayed` links of a `Position` cast, a trigger zone and a damage zone per trap, one set of flags per slot (champion-data "A trap that lasts, with three at once"); 12 s instead of minutes, gone when the caster dies | ~ |
| On-hit poison over time (Teemo E) | `AddCasted Poison` in the attack's projectile: every hit adds its own 4 s poison (League refreshes one), so the numbers count on the stack | ~ |
| Blind (Teemo Q) | `BlockAttack`: the target cannot basic attack; the game shows a disarm icon | OK |
| Invisible while standing still (Teemo's Guerrilla Warfare) | nothing reads stillness: `CasterInvisible` for 1.5 s with the move-speed skill, the attack-speed bonus beside it | ~ |
| Toggled aura (Amumu W) | on while fighting: every action starts a guarded train of `Delayed` pulses around the caster (champion-data "Aura that runs while he fights") | ~ |
| %-max-health magic damage (Amumu W) | `ApAttack` has no `target_hp_ratio`: the % part becomes `FixedAttack` (true), whole percents only | ~ |
| Amplify one damage type (Amumu's Curse: +10% of magic damage as true) | no per-type amplify field: `damaged_amplify` on all damage, re-applied so it never stacks | ~ |
| Hook that pulls the caster in (Amumu Q) | `LinearProjectile` on `EnemyChampion`: damage and `Stun` in `applied_effects`, `MoveToTarget` from a `Delayed` there (league_leesin Q2's way) | OK |
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
| Shield that hurts attackers (Annie E) | a `Shield` on her through a `RangeEffect` on `AllyOnlySelf` + a `WithShield` buff with `damage_reflect` (a share of every hit, basic attacks and skills, not League's flat hit once per attacker) | ~ |
| Summon that fights (Tibbers) | cannot walk or attack in data, but can ride on the unit he is cast on: a `Targeting` cast, an `AddCasted` on the target plays his pictures on it (`is_follow`) and lobs a one-tick burn circle round it every second, the target's death ends him (champion-data "A summon that follows its target"). He cannot pick a new target or chase one of his own | ~ |
| Refund on a kill (Annie Q) | detectable (kill trigger) and a short `skill_cooldown_mult` burst would speed the recharge, but it speeds every skill; league_annie leaves it out and keeps League's 4 s cooldown | X |
| Bonus on the first hit on a new target (Miss Fortune's Love Tap) | no "same target" test: the bonus comes when her last hit killed its target (kill check) or she has not fired for 1.25 s (champion-data "Bonus on a new target"); a switch while the old target lives gets none | ~ |
| Shot that bounces to an enemy behind the target (Miss Fortune Q) | two penetrating `LinearProjectile`s at one speed behind caster locks: the narrow visible bullet's first unit takes the shot, then the first unit an invisible wide twin touches within 7 ticks, after a 1-tick wait, takes the bounce (a narrow bullet alone rarely found a second champion); a kill check on the first makes the bounce crit (champion-data "The target and the next one behind it") | ~ |
| Channel broken by crowd control (Miss Fortune R) | queued `Delayed` waves run through a stun: each wave first looks for `AllyChampionInCC` within range 1 (the caster) and ends the channel; death ends it through a caster buff (champion-data "A channel that crowd control breaks") | ~ |
| Allies moving toward her go faster (Janna's Tailwind) | nothing reads which way a unit moves: while she fights, every action starts a guarded train of 1 s `move_speed_mult` buffs on `AllyChampion` around her (the Amumu aura) | ~ |
| Tornado charged up to 3 s (Janna Q) | the middle value: one penetrating `LinearProjectile` with `Airborne` 0.75 s | ~ |
| Shield an ally (Janna E) | a shield scores its full amount on anyone, so on an ally target the AI shields on cooldown, out of fights too (champion-data section 3); league_janna casts E on an enemy champion with W's gust folded in and shields the ally beside her, herself when alone (champion-data "Shield the ally beside her") | ~ |
| Cooldown refunded when she slows or knocks up champions (Janna E) | no effect resets a cooldown | X |
| Knock enemies away, then channel a heal (Janna R) | `Knockback` in a `RangeEffect` around her, then a buff-guarded channel of `Delayed` heals that crowd control or death breaks (champion-data "Knock them away, then channel a heal"); moving cannot end it | OK |
| Shield that returns after 10 s unhurt (Malphite's Granite Shield) | a `WithShield` buff tells whether it still holds; the next action after it broke starts a 10 s timer and the first action after that shields again (champion-data "A shield that comes back after it breaks"); a `Shield` cannot scale with max health: flat + `ap_ratio` | ~ |
| Armour-scaled damage (Malphite E, W) | no effect reads armour: `hp_ratio`, a share of the caster's max health, is the tank stat the data has | ~ |
| Attacks splash in a cone for a few seconds (Malphite W) | a caster window buff; while it lasts the attack adds a `RangeEffect` `Forward` + `DirDot` cone toward its target | OK |
| Unstoppable charge, knock-up where he lands (Malphite R) | `MoveToTarget` onto an enemy champion under a `cc_immune` buff, the knock-up circle in the dash's `end_effects` (champion-data "Charge onto a champion") | OK |
| Every third hit on the same target (Ekko's Z-Drive Resonance) | the caster counts his own hits (attacks, each Q pass, the E strike) on two 4 s buffs; the third procs on whatever it hit; the speed burst when an enemy champion is within 40000. No "same target" and no 5 s lockout per target | ~ |
| Device that flies out, holds a field, flies back (Ekko Q) | a penetrating `LinearProjectile` whose `end_effects` start the field and, after it, a `BackToCasterLinearProjectile` from that point back to him (champion-data "Out and back"); it always flies its full range | ~ |
| Bonus damage to low-health targets (Ekko W passive) | nothing reads current or missing health: dropped | X |
| Delayed sphere that bursts when the caster enters (Ekko W) | a lobbed hidden projectile starts the zones where an enemy champion stood; a zone checks every tick whether the caster is inside (`RandomTarget {AllyOnlySelf, from_projectile}`) and bursts once (champion-data "A sphere that bursts once the caster steps in"); folded into E with its own cooldown | OK |
| Dash, then the next attack blinks to the target (Ekko E) | one action: `MoveTo` onto the target (it goes all the way) and the strike in its `end_effects` | ~ |
| Rewind to where he was 4 s ago (Ekko R) | no position memory: an anchor dropped at the cast (a range-1 projectile's `end_effects` keep the spot) and a `Delayed` `Teleport` back there 4 s later, with the heal and the burst (champion-data "Back to where he stood"); the rewind's moment is fixed at cast + 4 s, and the heal cannot scale with the damage taken | ~ |
| Mixed damage on an AD hero (Yone's Way of the Hunter, W, R: part magic) | the engine's magic damage scales with ability power only and Yone has none: the magic part is `FixedAttack` (true) with an `attack_ratio`, at a lower ratio (the demon blade 50% physical + 40% true) | ~ |
| Leave the body, fight as a spirit, repeat the damage when pulled back (Yone E) | Ekko's anchor for the return, the body a `ViewEffect` of the sprite's own tag; champion-only twins of every hit queue a true-damage pop of a fixed share of that hit (nothing reads damage dealt), timed after the return by a ladder of caster buffs; the mark an `AddBuff` on the target lasting until its pop (champion-data "Leave the body"); folded into W every 15 s | ~ |
| Shield for each champion hit (Yone W) | a `Shield` among the champion cone's effects through a `RangeEffect` on `AllyOnlySelf`; shields add up | OK |
| Line that knocks up everyone on it, the caster ends behind the target (Yone R) | a `LineRangeProjectile` with `Airborne` after a 15-tick wind-up, then `RushMoveToBack`: he stops behind the chosen champion, not League's last champion hit, and does not pull them to him | ~ |
| Hook that stuns the first champion and drags him in (Thresh Q) | a non-penetrating `LinearProjectile` on `EnemyChampion` with `Stun` and `Grab` (no `tick`) in its `applied_effects`: the stunned champion is dragged to the caster; League's recast that flies Thresh to him is left out (champion-data "Hook the first champion and drag him in") | ~ |
| Lantern an ally clicks to be pulled in (Thresh W) | nothing can click: the lantern shields him and a random allied champion within 50000, folded into Q on its own cooldown | ~ |
| Fear on the first hit after standing still (Fiddlesticks passive; League places an effigy) | every action refreshes a 3 s combat buff; a cast without it arms a flag that the attack's champion-only twin and Reap's champion circle spend on a `Fear` (champion-data "Frighten on the first hit out of combat"); no effigy | ~ |
| Double damage on a feared target (Fiddlesticks Q) | a twin `TargetProjectile` on `EnemyChampionInCC` beside the crow carries the second hit: any crowd control counts, tested when it hits; the crow's own fear lands a tick later (champion-data "Double damage on a champion already in crowd control") | ~ |
| Drain tethered to every enemy near him, broken by distance (Fiddlesticks W) | a buff-guarded channel of `Delayed` pulses on everyone within 40000, each healing him through `Heal {heal_type: Caster}`; crowd control ends it; no tether to walk out of, but every pulse sends a soul-chain link from each drained unit back to him (champion-data "Strike, then drain everyone around him", "A tether picture on a range drain") | ~ |
| Channel, then fly to a point and storm around the caster (Fiddlesticks R) | a buff-guarded 1 s channel that crowd control breaks, `Teleport` to the cast point, then 5 s of `Delayed` pulses around him behind a buff his death clears (champion-data "Channel, vanish in crows, land in a storm") | OK |
| Walls round the caster, the one broken hurts most (Thresh R) | no walls round a caster (`Line` takes map coordinates): one circle, an `ApplyInProjectile` that hits each champion once; the first champion takes the damage and the long slow, a caster flag leaves the rest a short slow; the picture a `CasterViewEffect` (a `ViewEffect` on his own spot never showed in game) (champion-data "A prison that hurts only the first champion in it") | ~ |
| Push or pull by the cast direction (Thresh E) | the AI picks: pull within 2 s of a hook (League's hook-and-flay), else push (`Knockback`) when a champion is right on him and pull (`Pull`) when not, a `RandomTarget` flag read by `SwitchByBuff` (champion-data "Push or pull by the situation") | ~ |
| Souls picked up for armour and ability power (Thresh's Damnation) | nothing to pick up: armour and ability power growth per level | ~ |
| Skillshot blocked by the first unit, rooting it (Morgana Q) | the AI cannot aim round minions: a penetrating damage orb on `EnemyWithoutTower` plus a non-penetrating binding orb on `EnemyChampion` on one path; the bind's flag, a tick later, switches the damage off behind the bound champion; inside a `RandomTarget EnemyChampion` so it flies at a champion when one is in reach, and fast (10000 a tick: at League's slow speed the AI dodges 90%) (champion-data "Root the first champion") | ~ |
| Pool dropped on the rooted target (Morgana W after Q) | the zone in the binding orb's `end_effects` (where it stopped), behind a flag set by the bind and W's own cooldown; the "more damage to low health" part cannot be read | ~ |
| Spell shield with crowd-control immunity on an ally (Morgana E) | Janna's rule (cast on an enemy champion, the shield to the ally beside her) plus a `WithShield` buff with `cc_immune`: measured to block crowd control on the ally; the shield takes every damage type, not only magic | OK |
| Tethers that break out of reach and stun after 3 s (Morgana R) | every chained champion its own chain of 20-tick pulses: a hidden `TargetProjectile` from her, on its hit point `RandomTarget AllyOnlySelf from_projectile` (84000 = 1.68 x the cast radius, League's ratio) sets a flag that lets the slow, the chain picture and the next pulse go on; the ninth stuns; out of reach once, no stun; her death stops it (champion-data "Tethers that break out of reach") | OK |
| Heal from spell damage (Morgana's Soul Siphon) | no "damage dealt" to read: a `Heal {heal_type: Caster}` of a fixed share of each spell's numbers on every champion hit | ~ |
| Bleed that heals the caster, stacks capped (Briar's Crimson Curse) | `AddCasted Bleed` whose periodic effects hold a `Heal {heal_type: Caster}`: every tick of every stack heals her; the attack adds a stack at most once a second (a 60-tick caster lock), about five on one target; "heals more at low health" and the 5%-of-current-health cost cannot be read: dropped | ~ |
| Leap that stuns, then a frenzy with a recast bite (Briar Q with W) | one action: `MoveToTarget` onto a champion in reach (a `RandomTarget EnemyChampion` first, else the cast target, so it opens camps), the stun, the shred and a bleed in its `end_effects`, then a frenzy caster buff; the attack switches on it (60% on the target plus a 40% circle at `Forward` 18000 that holds the target); nothing presses the recast, so Snack Attack is the first attack 2 s into each frenzy (champion-data "Leap, stun, then a frenzy") | ~ |
| Scream that stuns whoever it knocks into a wall (Briar E) | no walls: a 1 s charge (a `damaged_reduce` caster buff, self-only heals), then a `DirDot` cone with `Knockback`, and on champions a `Stun` 16 ticks later when the knockback ends (the user's pick) | ~ |
| Kick that marks the first champion, fly to it, fear the others (Briar R) | a non-penetrating `LinearProjectile` on `EnemyChampion` (through minions) whose hit marks the prey and runs `MoveToTarget`; the landing gives the prey a 2-tick `cc_immune` buff before the fear circle, so only the others are feared (measured); the global range and "until one dies" became 120000 and 6 s (champion-data "Kick at the first champion") | ~ |
| Stream that bounces enemy - ally - enemy (Nami W) | every projectile leaves from the caster (only a `BackToCasterLinearProjectile` from a point, flying back to her), so the bounce is `RandomTarget from_projectile` searches round each hit and pictures on the units 9 ticks apart; a hidden lob at the ally looks for the last target round it; with nobody else near, the stream flies back to her from the first target; nothing marks a unit already hit, so the last hit counts enemy champions first and skips when the only one is the first target (champion-data "A stream that bounces enemy - ally - enemy") | ~ |
| Ally's next hits empowered, and they slow (Nami E) | nothing runs on another unit's attacks: `attack_mult` + `magic_power_mult` for 4 s on the ally W heals, the slow on W's own damage hits; folded into W | ~ |
| Allies hit by her spells move faster (Nami's Surging Tides) | a `move_speed_mult` `AddBuff` in every effect that reaches an ally: W's heal, and R's invisible twin on `AllyChampion` with twice the amount | OK |
| Slow that grows with the distance the wave rolled (Nami R) | a caster window buff from the cast, read by the wave's hits: the short slow while it lasts, the long one after | ~ |
| Ranks that unlock at levels (Kayle's Divine Ascent) | nothing reads a level but `SwitchByLevel3` (level 3): her maximum health is the level table, read with a 3-tick shield and a 10% max-health hit on herself; each rank a `Permanent` caster buff (champion-data "Stages at levels 5, 8 and 12") | ~ |
| Melee that turns ranged (Kayle's Arisen) | a `range` caster buff from that rank on, the attack's effect switched on the rank buff: a hit in melee, a `TargetProjectile` after | ✓ |
| Invulnerability on the one about to die (Kayle R) | no current health anywhere in the data, and the AI casts ally ults on cooldown on anyone: the slot (cast on an enemy champion as she closes in) arms it for 15 s and her attacks, Q and E check - a crowd-controlled ally within 50000 (`RandomTarget` `AllyChampionInCC`) first, else herself when two enemy champions are within 30000 (a two-flag count), else wait; unused, the cooldown is refunded. `damaged_reduce` 100 + `cc_immune` for 2.5 s, then the swords' damage round him (champion-data "An ult that waits for danger") | ~ |
| Orb out and back, true damage on the return (Ahri Q) | Ekko's out and back; every hit of the return first adds a 1-tick caster buff with `magic_resistance_penetration: 100`, so its `ApAttack` ignores magic resistance (`FixedAttack` cannot scale with ability power; champion-data section 4, "True damage that scales with ability power") | ~ |
| Fires that seek charmed champions first (Ahri W) | per fire three `RandomTarget` tiers - `EnemyChampionInCC`, `EnemyChampion`, `EnemyWithoutTower` - each leaving a 1-tick caster flag that skips the next tier (champion-data "Fox-fires, charmed champions first"); folded into Q on its own cooldown | ~ |
| Charm (Ahri E) | `Charm {tick}`: the target walks to the caster at its own move speed; crowd control for `EnemyChampionInCC` | OK |
| Three dashes, each firing bolts (Ahri R) | `cooltime_use_count: 3` on the ult (the AI spends the three within about 1.5 s in a fight); each cast dashes a fixed way - away (`MoveBack`) when an enemy champion is close, else toward its target (`RushTime`) - and fires three homing bolts, champions first (champion-data "Three dashes with bolts") | ~ |
| Heal on every hit after some spells (Ahri's Essence Theft, the pre-2022 one) | spells that hit count on caster buffs (one per cast behind a lock), the third charges a flag; the next spell turns it into a heal window and each of its hits heals the caster (champion-data "Heal on the hits of every fourth spell"). The current passive (heal on minion kills and champion takedowns) would need a kill check on every damage source and misses assists | ~ |
| Every third hit in a row deals %-max-health true damage (Vayne's Silver Bolts) | her own hits (attacks, the Tumble bolt, Condemn) count on two 3.5 s caster stacks - no "same target" test, as league_ekko's Z-Drive; the third deals flat `FixedAttack` true damage, and a champion-only twin of the bolt adds the `target_hp_ratio` part a tick later, so minions and monsters take only the flat part (League caps it on monsters) (champion-data "Every third hit deals true damage") | ~ |
| Move speed toward enemy champions (Vayne's Night Hunter) | no move direction: every action refreshes a 90-tick `move_speed_mult` caster buff (one instance) while an enemy champion is within 70000; Final Hour triples it | ~ |
| Tumble, the next attack stronger (Vayne Q) | league_lucian E's three ways (away from a champion on her, a hop back when an enemy is in attack range (all three 30000, League's proportion), else a fixed-length `RushTime` roll toward the target) and a 7 s ready buff the attack spends on a stronger bolt; no auto-attack reset (champion-data "Tumble by the situation") | ~ |
| Knock back; stun and more damage if it hits a wall (Vayne E) | no walls: the bolt's hit knocks back (away from the caster, measured) and a `Delayed` as long as the knockback hits again and stuns where the target lands, every time; a long knockback pushes the target out of her range (champion-data "Knock back, then stun where it lands") | ~ |
| Bonus attack damage, invisible Tumbles, extended by takedowns (Vayne R) | an 8 s caster buff (`attack_mult`, `skill_cooldown_mult` for both skills: nothing speeds one skill alone), `CasterInvisible` on each Tumble while it runs, Night Hunter tripled; league_jinx's kill check on her champion hits re-adds the buff at its full 8 s (her own kills only, a refresh instead of League's +4 s) (champion-data "A steroid that her kills refresh") | ~ |
| Next attack fires twice after a spell, the second shot weaker on champions (Lucian's Lightslinger) | charges as caster buffs (Q and R one, E+W two); the attack switches on them to a double shot with its own animation; a champion-only twin flags the second shot's champion hits, so only minions and monsters get its other half (champion-data "Two shots after a spell") | OK |
| Bonus magic damage on the next two attacks after an ally immobilises an enemy (Lucian's Vigilance) | nothing tells who applied a state: any enemy champion within 60000 in crowd control when he attacks arms two charges and a 1.5 s lock; each shot spends one on a hidden true-damage bullet (he has no ability power) (champion-data "Bonus on the next two attacks") | ~ |
| Dash to a point the player picks, either way (Lucian E) | three ways by the situation in one `Targeting` cast: away from a champion on him (`MoveBack`), a short hop back when something is in attack range, else league_ezreal E's blink toward the target that stops in range (champion-data "Dash away, hop back or chase into range") | ~ |
| Mark that speeds the caster up when he hits it (Lucian W) | the burst marks the target (a picture) and flags the caster; while the flag lasts every hit refreshes a 1 s haste, on any target | ~ |
| Beam from the weapon held at shoulder height (Lucian Q) | a `Targeting` cast: the damage on a `LineRangeProjectile` without a picture (it would be drawn at the waist); the picture on a slow `TargetProjectile` at the target, whose `y_offset` lifts only the picture, so it runs level from the muzzle; its frames one a tick drawn back against the creep; the hit at the end of the full glow, since the carrier goes when a killed target does (champion-data "A beam from a raised weapon") | ~ |
| Channelled barrage in one direction, blocked by the first unit (Lucian R) | 20 shots, each at the nearest enemy champion by rings of `RandomTarget`, a non-penetrating `LinearProjectile` on `EnemyChampion` (through minions); crowd control ends it (champion-data "Shots at the nearest champion") | ~ |
| Three recasts, the third different (Riven Q) | `cooltime_use_count: 3` and cast-counting caster windows (`q_1` -> `q_2` -> the leap, 4 s each); every cast a `MoveToTarget` hop with the slash round her on arrival, the third a knock-up; the AI weaves attacks between the casts by itself (champion-data "Three charges, the third cast different") | OK |
| Charges the next attacks spend (Riven's Runic Blade) | three caster buffs refreshed together on every gain, the attack spends the highest (champion-data "Runes the next attacks spend") | OK |
| Dash with a shield, then a stun round her (Riven E into W) | one `Targeting` action: the `Shield` through a `RangeEffect` on `AllyOnlySelf`, `MoveToTarget`, the damage and `Stun` circle in its `end_effects` | OK |
| Self-buff ult with a recast (Riven R, Wind Slash) | the slot arms it on the approach and it starts at the fight (a champion near the cast, else her first attack near one), refunded when unused; the recast fires by itself 5 s later at a champion in reach, `target_hp_ratio` for the missing-health part (champion-data "A self-buff ult armed on the way") | ~ |
| Weapon transformed while the ult lasts (Riven's reforged blade) | `_r` twins of the strips that show the weapon; every action picks its strip by `SwitchByBuff` on the ult's buff (the attack at `start_timing` 1 with its hit delayed); idle and run are the engine's and keep the old weapon, so an aura on the ult's buff marks it there (champion-data "The weapon reforged while the ult lasts") | ~ |
| Twilight Shroud (Akali W) | folded into E on its own cooldown, armed at the cast when an enemy champion is near: smoke where she lands and a fixed 2 s `CasterInvisible`, so she dashes back hidden; enemies next to her still see her. Invisible only inside a zone also works (Ekko's anchor, pulses renewing a short `CasterInvisible`), used while W rode Q (champion-data "Hidden for a fixed time on landing") | ~ |
| Flip back, mark, recast to dash to the mark (Akali E) | `MoveBack` in a `Targeting` cast, a skillshot from the landing spot, and the dash automatic 0.5 s after the hit (Lee Sin Q2's `Delayed` `MoveToTarget` in the projectile's effects), skipped under crowd control | ~ |
| Second dash that executes by missing health (Akali R2) | nothing reads health: the second dash, 2.5 s after the first, deals +25% per champion hit she landed in between (max +200%), at the first target when it lives and is within reach, else at another champion near her (champion-data "Two dashes") | ~ |
| Leave the ring to empower the next attack (Akali passive) | a champion hit by a spell arms a `range` + move speed caster buff for 4 s; the next attack from double range consumes it | ~ |
| Every third attack cleaves, attack speed after spells (Diana's Moonsilver Blade) | two caster stacks walk the attack; the third plays its own strip and adds an `ApAttack` circle at `Forward` that holds the target; every spell refreshes a one-instance attack-speed buff (champion-data "Every third attack cleaves") | OK |
| Mark the next dash resets on (Diana's Moonlight + Lunar Rush) | target buffs cannot be read: any Crescent Strike hit sets a 3 s caster flag (the unit gets only the picture); Lunar Rush with the flag dashes twice in one cast, the second at a champion near her first (champion-data "A mark the caster reads", "A dash that refreshes on the mark") | ~ |
| Orbiting orbs that burst on contact, the shield grows after the third (Diana W) | folded into E's arrival on its own cooldown: a shield, then pulses that fire one orb at a random enemy in reach; the orbit is a caster buff per count; the third re-shields (champion-data "Orbs that burst one by one") | ~ |
| Pull nearby champions, a delayed blast that grows per champion (Diana R) | `Grab` without `tick` in a `RangeEffect` on `EnemyChampion`, a three-flag count, the blast 1 s later picked from a ladder; the pull reaches well past the cast range (50000 against 25000: the AI casts from range plus both bodies) (champion-data "Draw them in, then the moon crashes") | OK |
| Attack speed stacks lost one at a time (Jax's Relentless Assault) | every attack finds the count from the top stack down and adds all again, one more, their durations growing toward the bottom stack, so they end one by one (champion-data "Attack speed that stacks and falls off") | OK |
| Next attack or next leap empowered, on its own cooldown (Jax W) | a cooldown caster buff; the attack picks its smash on tick 1 and flags the hit, the leap's landing spends it the same way | OK |
| Leap to an ally or a ward to escape (Jax Q) | the AI casts on enemies only; the leap goes to the AI's own target (a champion, a minion or a monster) - a random champion first dived into the back line | X |
| Dodge every basic attack for 2 s, then stun around (Jax E) | `base_attack_damaged_reduce: 100` plus `skill_damaged_reduce` for the area part while he keeps fighting, then a buff-guarded `Delayed` stun circle; the bonus per dodged attack cannot be counted, no early recast | ~ |
| Armour and magic resist per champion hit (Jax R) | the champion circle's effects add a caster buff per unit hit: the first a base buff, every other an extra one | OK |
| Every third attack, every second while the ult lasts (Jax R's passive) | two caster counters refreshed by each attack; the ult's buff shortens the chain | OK |
| Ability power that grows for good (Veigar's Phenomenal Evil Power) | one more `Permanent` `magic_power: 1` caster buff per stack (instances add up): his spell hits on champions, Q's kills (the kill trigger), champion kills +5; death clears them - no native passive of 0.6 stacks ability power (champion-data "Ability power that stays until he dies") | ~ |
| Skillshot through the first two enemies (Veigar Q) | a penetrating `LinearProjectile` whose applied effects count the hits on two caster flags | OK |
| Cage that stuns units crossing its edge (Veigar E) | a disc: an `ApplyInProjectile` stuns every unit once as it touches it, those inside when it forms at once; W folded in lands on its centre (champion-data "A cage that stuns whoever touches it") | ~ |
| Damage by the target's missing health (Veigar R) | +25% per spell hit landed on champions in a row before it (each within 4 s of the last), max +100% (champion-data "R stronger for every spell hit in a row") | ~ |
| Empowered attacks after every spell, each cutting the cooldowns (Taric's Bravado) | two caster charges and an attack-speed buff from every spell; the cut as growing 2-tick `skill_cooldown_mult` bursts (55, 145), `ult_cooldown_mult` of the opposite sign keeping the ult out (champion-data "Two quick attacks after every spell") | ~ |
| Stacks that fill over time (Taric Q) | three caster timers read at his actions (a stack for each 5 s since the last grant), Bravado hits add one; cast on `EnemyWithoutTower` near him so it goes off in every fight | ~ |
| Spells also cast from a linked ally (Taric W) | an `AddCasted` on the ally reads his cast flags every tick and lobs a hidden projectile onto the ally to start the Q heal, an E stun circle (no beam can leave from the ally) or the R circle there, only while the two are 30000-110000 apart (champion-data "A link that repeats his spells") | ~ |
| Line stun after a delay (Taric E) | `LineRangeProjectile` with `apply` 45, a wider line, and as long as the AI casts it (80000): League's 1 s let walking champions out, a 62000 line let them back off past its end | OK |
| Team invulnerability after a delay (Taric R) | armed on the approach, started at two enemy champions or a crowd-controlled ally near him; `damaged_reduce` 100 for 2.5 s after 2.5 s | ~ |
| Attack range that grows with level (Tristana's Draw a Bead) | +2500 `range` at levels 3 (`SwitchByLevel3`), 6, 9 and 12 (league_kayle's health probe, run only in her skill slots - an attack's `FixedAttack` crits - under a 99% damage reduction, two passes in a fight); no stage came early in the simulation, some came late (champion-data "Attack range at levels 3, 6, 9 and 12") | ~ |
| Units her basic attacks kill explode (Tristana's Explosive Charge passive) | a hidden lob fired with the shot lands where the target stood and reads league_jinx's kill check there (champion-data "Units her basic attack kills explode") | OK |
| Charge that her hits stack, detonating on the fourth (Tristana E) | the count on caster flags, polled by an `AddCasted` on the carrier; any of her hits counts (nothing tells which unit a hit is on); Q's attack speed folded in (champion-data "A charge that sticks") | ~ |
| Jump to a spot, reset by takedowns (Tristana W) | no player: her shots set it off - onto a champion whose charge holds 2-3 stacks, away from champions on her; its cooldown a caster buff her champion kills and full-stack detonations remove (champion-data "A jump her shots set off") | ~ |
| Knock back the target and those around it (Tristana R) | a blast circle round the target a tick after the hit: `Knockback` away from her, a `Delayed` stun where they land | OK |
| Vitals on one side of the target, struck by a hit from that side (Fiora's Duelist's Dance) | her own caster flags: 3 s after a Vital was struck her next champion hit reveals one and the next strikes it (true damage with % max health, a heal, fading move speed); no side can be read and no state kept on the target (champion-data "A weak spot on the target") | ~ |
| Dash-stab, then two empowered attacks (Fiora Q with E) | `MoveToTarget` onto a champion in reach first, else the cast target; E on its own cooldown buff arms a slowing first attack and a 160% critical thrust | OK |
| Parry that stuns only if it blocked crowd control (Fiora W) | `damaged_reduce` 100 + `cc_immune`, and a 1-point shield: its break (a `WithShield` flag gone) turns the stab's slow into a stun, so any blocked hit counts | ~ |
| Four Vitals, a healing zone when all are struck or the target dies (Fiora R) | an armed ult (the AI casts early); four rung flags, each champion hit takes one and caps Q's and W's cooldowns at half, so the pace follows the fight; the zone lobbed onto the target, or on her spot when the target died (alive-gated picture pieces) | ~ |
| Untargetable hop that dodges what comes, or an engage slam (Fizz E) | held up to 1 s while enemy champions are near and released by the first hit on him (a 1-point shield's `WithShield` flag, polled by one zone round him), then `CasterInvisible` + `damaged_reduce` 100 / `cc_immune` for the vault and a slam on the nearest enemy; at once on waves and camps (champion-data "A hop held until the first hit") | ~ |
| Fish that sticks, the shark sized by the distance (Fizz R) | caster windows from the throw give the flight time at the hit, a `Delayed` lob onto the stuck champion 2 s later starts one of three sharks; a miss leaves the big one where the fish stopped (champion-data "A fish that sticks") | OK |
| Next attack empowered, its cooldown cut by a kill (Fizz W) | a cooldown caster buff; league_jinx's kill check on the strike swaps it for 1 s; the strike also rides Q's hit | OK |
| Moves through units (Fizz's Nimble Fighter) | no field (BuffState's only movement flag is `ignore_wall`); the damage reduction from basic attacks is `base_attack_damaged_reduce` | X |
| Vanish, blink behind the target, the next attack a critical backstab (Shaco Q) | `CasterInvisible` + `RushMoveToBack` (15000 past the target); a caster flag picks the attack's backstab, which adds a 2-tick `crit_chance` 100 caster buff just before its `Attack` (champion-data "A blink behind the target") | OK |
| Backstab from behind (Shaco's passive) | nothing reads facing: Q's landing hit, hits on champions in crowd control (an `EnemyChampionInCC` twin: a feared champion shows its back) and the clone's strikes (champion-data "Backstab without facing") | ~ |
| Poisoned dagger throw (Shaco E) | folded into the attack on its own 8 s cooldown flag: the next attack plays its own strip and throws a magic-damage shiv that slows | ~ |
| Hidden box that fears, then shoots (Shaco W) | a `Position` cast lobs it to the enemy's feet; it pops at once (no stealth, no waiting): `Fear` on champions with a 2-tick `cc_immune`, a tick later a longer one on the rest, then a `RangePeriodProjectile` shoots 5 s (champion-data "Two fears from one box") | ~ |
| A clone he can steer, exploding into boxes when it dies (Shaco R) | an `AddCasted` on the target champion draws the clone, which strikes with his hits or every second; it explodes after 5 s or where the target died (a lob read against a refreshed flag), leaving three mini boxes; it cannot walk, be attacked or die (champion-data "A clone that rides the target") | ~ |
| Every Nth shot empowered, a trapped champion shot first at longer range (Caitlyn's Headshot) | counter caster buffs walked from the top; while her trap holds a champion, a `RandomTarget` on `EnemyChampionInCC` within 1.5x range takes the shot; a net hit arms the next one (champion-data "Every sixth shot a Headshot") | ~ |
| Net that slows and hops her back (Caitlyn E) | folded into the attack: an enemy champion within 25000 and E ready make the shot the net, then `MoveBack` from him (champion-data "A shot that becomes the net") | ~ |
| Traps with charges, each rooting the first champion on it, spread out (Caitlyn W) | league_teemo R's three slots on a `Direction` cast: slot a's throw stops on the first enemy champion, b and c land at fixed distances on the aim line; the zone takes its slot's `alive` flag first (one champion bitten) and asks `RandomTarget {AllyOnlySelf}` whether she lives (zones from `end_effects` outlive her); an empty branch while a snapped champion is held keeps the AI from throwing the rest at him | OK |
| Skillshot fired after a wind-up, dodged by moving (Caitlyn Q) | the aim locked a few ticks before the shot: a hidden `ParabolicProjectile` lands where the champion stood and its `end_effects` fire the bolt from the caster at that point; locked at the cast start the AI's walking champions dodged 84% (champion-data "A piercing round at where a champion stood") | ~ |
| Long-range shot after a channel, blocked by the first champion (Caitlyn R) | league_missfortune R's crowd-control check, then a non-penetrating `LinearProjectile` on `EnemyChampion` toward the target | OK |
| Every few attacks a cleave round him that heals per enemy (Nocturne's Umbra Blades) | every 12 s or on the fourth attack: a cooldown caster buff and three counter rungs; the cleave plays its own strip, a circle of 120% attack and a heal per enemy hit (champion-data "A cleave every fourth attack") | OK |
| A trail that speeds him while he stands on it (Nocturne Q) | the blade's path drawn on the ground (picture-only on `Ally`) with zones along it, and the champions it hit trailing one (a polled `AddCasted`); on it, one refreshed move speed + attack buff (champion-data "A trail that lies on the ground") | OK |
| Tether that fears if he stays in range (Nocturne E) | links flying back to him (league_fiddlesticks W), damage pulses, a check projectile after 2 s: still near -> `Fear` and his move speed (champion-data "A tether that fears if it holds") | ~ (the AI does not stay close: half the checked champions are in reach) |
| Spell shield, attack speed when it blocks (Nocturne W) | folded into E: skill damage cut to 1, `cc_immune`, a 1-point shield whose break (a `WithShield` flag gone) gives the doubled attack speed; any hit counts, basic attacks too (champion-data "A spell shield that pays out") | ~ |
| Darkness that takes the enemies' sight, a dash from far away (Nocturne R) | no vision field: every allied champion `Invisible` for 3 s and a mist picture on the enemy champions, then `MoveToTarget` from 110000 with `cc_immune` (champion-data "Team invisibility and a dive") | ~ |
| Hook the first champion through minions and bring him back to the arm (Blitzcrank Q) | league_thresh Q's hook (a non-penetrating `LinearProjectile` on `EnemyChampion` with `Stun` and `Grab`); an `EnemyChampionInCC` twin tells a held hook from a blocked one, caster flags from the throw tell the hook's end and the twin how many ticks it flew: the drag stops the catch in front of him as the hand gets back to his arm, and two projectiles on the hook's own line carry the hand and its chain back (champion-data "A hook from a raised arm that brings its catch back along its own line") | OK |
| Burst of speed that decays, then a slow (Blitzcrank W) | folded into E on its own cooldown: his first action with an enemy champion within 60000 starts it; two move-speed caster buffs (fast, then less) and attack speed for 4 s, a self-slow after (champion-data "Overdrive folded into the uppercut") | ~ |
| Next attack knocks up (Blitzcrank E) | an uppercut action of its own on a champion in reach first, else the cast target (waves and camps too): damage and `Airborne` 1 s | ~ |
| Lightning after attacks while the ult is ready, a silencing burst (Blitzcrank R) | the attack's carrier marks the unit and a `Delayed` bolt strikes 1 s later unless the `r_cd` caster flag the cast sets for the ult's cooldown is there; the active armed like Taric R, `BlockSkill` 1 s on champions (champion-data "The ult's passive while it is ready") | OK |
| Shield at low health (Blitzcrank's Mana Barrier) | nothing reads current health: two enemy champions near him or him crowd-controlled (pulses after every action) set it off, 60 s cooldown (champion-data "A shield when in danger") | ~ |
| 2-3 stage recast | `cooltime_use_count` or recast buff + `SwitchByBuff` | ~ (AI timing) |
| Cone / fan of projectiles (Ashe W) | no angle field on any projectile (base harpooner's fan is `Native`): a `LineRangeProjectile` rectangle cast by `Direction`, drawn as a fan sprite centred on it (champion-data "Cone / fan"); the hit area stays a rectangle | ~ |
| Untargetable / invulnerable | `Banish` on self (a `RangeEffect` on `AllyOnlySelf`; it also makes the unit invisible, puts a CC state on it, stops the caster's own `RandomTarget` finding units and takes away its team's vision around it - only for a caster leaving the fight); in a fight `CasterInvisible` + a `damaged_reduce` 100 / `cc_immune` buff: targetable, but every hit deals 1 | ~ |
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
Since game 0.6 the classic SDK is no longer shipped, so the simulator links game_core 0.5.1, the last one; the
settings and the champion sheet it loads are the 0.6.2 bundle's, byte for byte, but whatever the engine's code
changed after 0.5.1 is not in it (champion-data section 9): check a close call in game.

Rerun it once the art has set the timings. league_annie was balanced at +1.24 kills (24 seeds a
lineup) with placeholder timings; aligning her casts with her strips (the fireball thrown on tick 12
instead of 18, a shorter attack) and landing Tibbers on his picture's impact frame (6 ticks after the
cast instead of 18, so fewer targets walk out) lifted the same numbers to +1.95, and the final
tuning was done on those timings (+1.49). league_missfortune the same way: +3.99 with placeholder timings
(24 seeds a lineup), +5.50 (36 seeds, two kills above the best base marksman) once her shot, Double Up,
Make It Rain and Bullet Time fired on tick 8 of their strips instead of 10-12; her nerf was chosen on
the final timings. A mechanic fix gets the same rerun: Double Up's wide twin (three times the bounces
onto champions) came out at +4.39 against +4.41 on the same seeds, so no numbers moved.

One batch is noisy: the same league_annie 0.13.0 kit gave +1.49 on seeds 1-24 and +2.22 on seeds 25-48
(720 games each, 5 opponents x 3 lineups x 2 sides), while its damage dealt moved only from 12512 to
12629. A candidate ranked by one batch can come out upside down (her 0.13.1 burn: 10 + 6% +1.91 above
14 + 8% +1.57, with damage 12682 below 12843). Compare candidates on two batches of different seeds and
read the damage dealt next to the kill difference; the simulator is deterministic, so a kit rerun on the
same seeds gives the same numbers and the old kit need not be rerun on seeds it already played. But any
change reshuffles the games: league_ahri's R bolts at 38% of ability power gave +2.07 on seeds 1-24, at 40%
(nothing else changed) +3.04 on the same seeds (damage 12984 -> 13916) - as far apart as two seed batches of
one kit. Judge the shipped kit on both batches (hers +3.04 / +2.27) rather than on the candidate it came from.

When a first draft is far off, take it apart before tuning. league_malphite (top, against the six base top
laners) opened at +4.38 kills with 0.6 deaths a game (base fighter +0.93, Darius +1.43, Teemo +1.18 on the
same seeds); four 432-game candidates, each cutting one side of the kit, showed where it came from: his
tankiness (armour, the shield) -0.2, his damage -2.0, his crowd control (R's knock-up and cooldown, the slows)
-1.6. The final kit keeps the tank and trims both, and its last step was the knock-up alone: 1.25 s gave +1.01
where League's 1.5 s gave +1.80 (864 games each). Rerun on the strips' timings (his fist lands on tick 8, the shard leaves on 12, the slam on 11, the R's damage 4 ticks after he lands) it read +1.31 and +1.63 on two seed batches, the base fighter +0.93 and +1.08; Ground Slam's health ratio 3% -> 2% gave +0.91 and +1.02.

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
  path that follows. `python tools/lol/anim_graph.py <Champ> [--grep run]` parses the whole bin and
  prints every clip with its file, its cycle (frames x `mTickDuration`) and, for the logic clips, their
  branches (Yone: `Run` = `run_homeguard` under the homeguard buff, else `run_base` = `Yone_Walk01`,
  1.09 s; Ekko: `Run` = `run_base` = `PunkGenius_Run1`, 1.07 s, from move speed 315, `Run_Haste` from 535;
  Ahri: `run_base` is a sequence, `Run.anm` once and then a selector of `Run.anm` 50%, `Run_Var1` and
  `Run_Var2` 25% each - the tool prints a sequence's clips and a selector's chances, and an unnamed clip as its
  hash with its file, `#cc7e3fac=Run.anm`). Ashe: `Run` = `ashe_run_walk`, `Run2` = `ashe_run_jog`, `Run3` = `ashe_run`;
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
- **A tricorne over a drawn face (Miss Fortune, drawn by Claude, restyled, head pasted).** Her `Hat` joint
  hangs under `Head`, so `--head` grows the hat with the face: at head 1.7 the tricorne took ten of her 35
  rows and the face four. `"chibi": {"head": 2.1, "scale": {"Hat": 0.75}}` gives a face big enough for
  three-row eyes under a hat that still reads as a tricorne (legs 0.65, hair 0.5; camera yaw 35, not
  mirrored, both pistols as the weapon part `^[lr]_weapon$`). Her 36 px count the hat, like the base gambler
  (36) and gunner (37), whose face points sit just under their hat tops; hers is (1, -34). The head was drawn
  over the design pose voted whole - hat, hair and skin by materials - then square by square: a wider hat
  with two points and a gold band, a fringe, blue eyes, a dark-red lip, and the far side's hair puffing past
  the cheek (a straight edge there reads as half a head on the dark card). Of three faces the user took C
  (three-row eyes with a winged lash row, the lip), then called that lash row a black clump: outline-black
  squares right under the fringe merge into one bar. Dark red-brown lashes without the wing fixed it (C1).
  League's death throws both pistols away and ends face down with her legs kicked up over her head: the guns
  are hidden per frame once they leave her hands, the pasted head stays upright (`"turn": {"dead": 180}` in
  the restyle spec), and the strip stops at 3.4 s, lying on her stomach with her head up - past that, a
  quarter-turned head or an upright one sat on top of the raised legs. 49 frames, 23 colours, 35%
  right-neighbour. Her twelve effects came from Codex as raw generations with a manifest
  (`assets[].frames[].source_rect`); Bullet Time's wave came on black, so `tools/art/import_missfortune.py
  --raw` takes its alpha from the brightness, and anchors the wave on one fixed column of every cell (the
  muzzle of frame 1): anchored on each frame's own left edge, the seven bullets would stand still instead
  of flying out. The wave is squeezed to the kit's 100 x 72 px (a 40 degree fan over the 100000-long
  rectangle, its muzzle 50 px behind the rectangle's middle); the rain's ring is 60 px wide (radius 30000).
  The rain first played as its zone's view, which is turned with the cast: cast leftward (the user saw it
  in the mid lane, cast one way along it) the bullets fell upward. It now plays as a `ViewEffect` on the
  cast point, never turned, and the zone has no view (champion-data section 6).
- **A floating support with a flame of hair (Janna, drawn by Claude, restyled, head pasted).** League's Janna
  floats: 12 to 39 units above the floor in idle, a glide in the run that rises and falls 47 units over its 2 s
  cycle, 64 units up in Monsoon. `"hover": 3` keeps every frame 3 px above the ground (the user's pick of 0 / 3
  / 6 px; the base ghost floats about 6), the run keeps `"rise": 0` with `"flat"` (League's float gone, the
  legs' lowest point on the feet line), the ult `"rise": 0.4`, and the death `"sink"`s 1-3 px as she lands.
  The run first kept 70% of League's glide: her body leaned forward with the legs trailing, the lean changed
  from frame to frame under the upright pasted head, and in game the user saw the body move under a head
  that stayed put ("头像脱节了一样"). Of runs blended 45 / 60 / 85% toward the idle pose (a looping GIF side
  by side with the old one) the user took 85%: she floats along nearly in her idle pose, skirt and legs
  trailing a little, like the base ghost.
  Proportions (the user picked D of four at game size): 28 px crown to soles, chibi head 2.0, hair 0.5, legs
  0.8; her swept-up hair stands 7 px above the crown, so she is 33 px tall (the base priest 35). At that size
  her arms, legs and cloth strips are one or two pixels wide, and the outline drawn round each cut her into dark
  stripes (as many outline pixels as body pixels): restyle's `"cover": 0.3` (a block opaque from 30% of its
  pixels) and `"close": 1` (a gap between two body pixels filled) made her skirt one white shape, and
  `"weapon_materials"` keeps the staff's orange gems apart from its blue. League's own face at head 2.0 was four
  by three pixels under the hair, so the head was drawn square by square: the swept-up flame from League's head
  voted at game size (a clean wedge, given three tips and streaks so it reads as hair and not a witch's hat), a
  round chibi face after the base spirit caller's (6 wide, base eyes with blue irises), the blue diadem and its
  crystal, the pointed ear behind. Of three faces the user took B, one dark-red mouth square. Camera yaw 45,
  mirrored (unmirrored, her staff crossed her face). Her death lies at tilt -47 to -65, so `"turn": {"dead":
  45, "*": 180}` quarter-turns the head in the lying frames only. In game the user then saw her head apart
  from the body in Monsoon, joined by "a pipe": the pasted block carried two rows of the design's neck
  (drawn on the idle body, an outline down its middle), and Monsoon turns her torso side-on, three pixels
  wide under the 14 px head. Of three fixes at 11x and in game size (a clean one-row neck; that and a wider
  chest; no neck and a wider chest) the user took the last: the block ends a row under the chin, that row
  painted one piece of skin (`"paint"`), `"dy": -2` seats the chin on the shoulders (it was -4), and
  `"shoulders": {"x": 10.5, "widths": [7, 6, 6]}` widens the three rows under the block before the head
  goes on (art-spec). The face point moved down with the head (-31 to -29). 52 frames, 27 colours, 30%
  right-neighbour.
  Codex's eleven effects came as raw generations (manifest `janna-fx-raw-handoff-v1`, `assets[].frames[].rect`
  as {x, y, w, h}); `tools/art/import_janna.py --raw` scales them to the kit (the vortex 26 px, both Monsoon
  rings 84 px wide, the ground storm squeezed from 1.47:1 to 2:1) and anchors the tornado on its vortex's
  centre, its hitbox. A projectile's picture turns with the cast direction, so Howling Gale was asked for as a
  vortex seen from above, not a funnel that would fly upside down to the left. The storm shield is a
  `ThreePhase` buff picture (champion-data section 6).
- **A monster whose head hangs in front of its chest (Malphite, drawn by Claude, restyled, head pasted on
  the shoulders).** League's Malphite is a mountain of stone plates over crimson flesh with a crest of pale
  spikes; his head (the `head` part of a `--parts` render) is a rhino-like snout with one huge horn and a
  small glowing eye, 6 px wide in the middle of his chest at game size. Scaled up (`chibi` head 1.6-2.6) or
  voted by materials it melted into the chest's stone, so the head is drawn and pasted. What the user
  rejected, three faces at once: a smooth round ball with a face on it (glowing slits, round eyes with a
  mouth, a magma mouth) read as a mascot, pale like a sticker, its thin horn an ear, and it broke the "small
  head, huge body" read. What was accepted (V12a): the head as League builds it, seen from the side like
  oppi's Alistar and Sion in LoL Reborn - a dark stone snout pointing right with a thick pale horn rising from
  it, standing in the empty air in front of the spike crest (placed right of the crest so the horn is not
  lost against the spikes), one glowing eye under a heavy brow, pale plate tops, cracks and a dark collar
  round the horn's base. League's head stays in the frame, voted as chest stone (`"under"`), so the drawn
  head leaves no hole. Pasted on League's head joint (19 rows above it) it floated off the body in 9 of 55
  frames, wherever the small head nodded or swung apart from the shoulders (the attack's wind-up, the ult's
  landing, the death); `"anchor"` (native_pose) and `"head": {"anchor": true}` (restyle) put it on the
  shoulders' midpoint instead and turn it with the torso (pelvis to shoulders), and a contact count (head
  pixels touching the body, lowest 22) checked every frame. Camera yaw 35 unmirrored, legs 0.85, height 26
  (the head top is League's; 45 px with the spikes, the base ogre's 44), the R landing on the crit clip's
  smash (League's `RunUlt` is only the charge), idle one frame breathing, the run 40% toward the idle (the user's
  pick from three looping runs: League's hunched charge made him look small), 54 frames, 14 colours, face (4, -42).
  Codex's ten effects came as raw generations with a manifest (`assets[].frames[].rect` as [x, y, w, h], the
  frames not all equally wide); `tools/art/import_malphite.py --raw` measures each strip's scale on the drawings
  themselves (its widest drawing, or the tallest for the knock-up's eruption, brought to the kit's size) instead
  of source sizes typed in: the slam's ring 72 px (radius 36000), the crater 64 px, the shield's ring of stones
  50 px round his body, Thunderclap's two arcs 40 px apart at his fists.
- **A crouching boy with a mohawk (Ekko, drawn by Claude, restyled, head pasted).** League's Ekko idles in a
  deep crouch with his bat pointing forward and his head bowed; the user picked his crouch at 90% (B of four:
  the crouch, the crouch at 90%, half upright, upright - `"height"` 28 from the skull to the soles, 34 with the
  crest, about 500 px of body next to the base swordman's 472) over the more upright poses. His mohawk hangs on
  `F_Mohawk1` / `B_Mohawk1`, which the hair rule (`hair|braid|ponytail`) misses, so `"chibi": {"scale":
  {"F_Mohawk1": 0.6, "B_Mohawk1": 0.6}}` shrinks it and `"crown": 181` measures the height from the skull.
  The lit render turns his dark brown skin mauve-pink: League's texture has it at `#63383C`, and the restyle
  ramps take the texture's colours. The head: three first faces drawn from scratch (a round head, a flat face,
  a white crest on a grey-green cap like a helmet, a paint streak read as a third eye) were all rejected as
  strange and low in quality, and a game-size vote of League's head was mush (the face 9 px wide under the tall
  crest). Accepted: the head drawn square by square on the base swordman's head - white spiky hair seen 3/4
  right, 12 wide - with its two-tone strands and three-row eyes, the hairline down to the brows (a five-row
  face), the crest leaning forward like League's, the shaved sides a mid tone with two shave lines, one
  dark-red mouth square (B of three; League's white face paint was left out). Pasted on League's head joint,
  upright in every frame (`"turn": 180`: his death throws the head back past 60 degrees while he still stands).
  Camera yaw 45 unmirrored, the Z-drive on his back a part of its own (`^Weapon_Back`, blue and steel), the
  run League's own `Run1` (his `run_base`) at League's pace, 8 x 133 ms = 1.07 s (first blended 60% toward the
  crouch at 1.06 s a cycle: in game the user saw him slide, "像僵尸步"; then 8 x 80 ms against the slide, until
  the user saw the pace differ from League's - see art-spec "The move is League's movement clip at League's
  pace"), idle one frame breathing; 51
  frames, 40 colours, face (10, -32) - he crouches
  forward, so the head is 8 px ahead of the pivot. Chronobreak's hologram at the anchor is his idle drawing in
  the rewind skin's mint with scan lines, made by `tools/art/import_ekko.py` rather than by Codex.
- **A masked swordsman with two blades (Yone, drawn by Claude, restyled, head pasted).** League's Yone skin
  carries submeshes his base look never shows (the Azakana, props, the blades' smear trails, the sheath, an
  inner skirt) and his two katanas take a texture of their own, `Swords_TX`. `pose_ref.py` / `native_pose.py`
  gained two options for that, off by default (every other hero renders byte-identical):
  `"hide_submeshes"` as a list of names (`--hide-submesh NAME`) and `"submesh_textures"` (`--submesh-texture
  Katana=Swords_TX`). The steel katana is the `weapon` (`^sword$`), the red demon blade a part of its own
  (`^ghostsword$`). Three heads at 12x; the user took A, League's own: the red V mask over the upper face, two
  horns (one swept back, one up), glowing violet eyes under it (the near one 2 px, the far one 1), the long
  black hair tied back with a lock by the cheek, the pale lower face without a mouth. 41 px with the horns
  (37 without), about 500 px of body - the base swordman 472, the dual blades 503, league_yasuo 602. Pasted on
  League's head joint, the big head hid the body in the crouched frames (Mortal Steel's thrust, the Q3 dash,
  Spirit Cleave, Fate Sealed's wind-up), so those blend 30-40% toward the idle; the death's second frame turned
  the head a quarter round (`"turn": 180`), Spirit Cleave's hop is lifted 0.2 (`"rise"`). Camera yaw 35
  mirrored, head 2.0, legs 0.8, hair 0.5; the second attack is League's
  `Attack02` with the demon blade as its own tag (`attack2`); the body left behind in Soul Unbound is
  `Spell3_bodyLoop` as a tag (`e_body`, 2 x 2000 ms); the move League's `Yone_Walk01`, his `run_base` (the
  graph's `Run` plays it except under the homeguard buff; `Yone_Run01` is `run_fast`, not his move), 8 x
  136 ms = 1.09 s, League's pace (38 frames at `mTickDuration` 1/35) - until the user saw the posture and the
  pace differ from League's, it was `Run01` at 8 x 80 ms (see art-spec "The move is League's movement clip at
  League's pace"); idle one frame breathing; 75 frames, 30 colours, face (-1, -39).
  Codex's sixteen effects came as raw generations on near-black opaque canvases (manifest rects [x, y, w, h];
  Mortal Steel's five frames unequally wide). `tools/art/import_yone.py --raw` keys the black by the brightest
  channel (League's dark ink `#1E1648` survives), samples on pixel centres and mirrors the upper half of the four
  line pictures (the thrust, the gust, the fan, the slash) so the game can turn them over, anchors the thrust
  on each frame's tail (its last frame's streaks at the full lance's tip), rides the gust on his dash with its
  front 22 px ahead, and cuts the mark into an intro, a loop and a dimmed end for a `ThreePhase` buff that lasts
  on the enemy until the burst. The auras round his body sit 2-3 px left of the pivot: his katana hangs on the
  right, so his body's middle is 3 px left when he faces right.
- **A skull in a robe with a scythe and a lantern (Thresh, drawn by Claude, restyled, hand-drawn head
  pasted).** The user took C30 of three proportions and two heights (head 2.0, legs 0.8, hair 0.5, height 30;
  39 px with the chains on his head). The lantern is a part of its own (`^lan_chain\d$`, its glass voted by hue
  60-185 onto a yellow-green soul-light ramp), the legs too (`^[lr]_kneeupper$`, dark purple, so the stride
  shows under the robe), the scythe and its chain the `weapon`. The head took four rounds: three faces drawn
  from scratch were rejected ("A B C 都不及格"; the user liked League's own head, voted, better); the voted head
  was then "好模糊" at game size, and more detail in the vote stayed blurry ("细节还模糊 实在不行你就手画");
  three skulls drawn square by square on League's structure followed, and the user took C: a dark purple
  skull 11 wide, V-shaped brows running down to the nose, two glowing green eyes, three fangs (the outer two
  long) over a green-lit maw, and two chains with teal joints arching back from the crown to a hook. Pasted on
  League's head joint and kept upright (`"turn": 180`); `import_native.py` steadies him on that joint
  (`PASTED`). The move is League's walk: the graph's `Run` plays `run_base` = `Thresh_run` (after
  `Thresh_run_in`) at base speed and `run_fast` only from move speed 375 (`anim_graph.py Thresh --grep run`);
  the 2 s file holds the same 1 s walk cycle twice. The user asked for "一模一样在游戏里的走路姿势" (the first
  version read as a run) and set 8 x 125 ms, one cycle a second - League's pace (art-spec "The move is
  League's movement clip at League's pace") - unblended.
  Idle one frame breathing (the robe's hem moves, the boots stay), 55 frames, 35 colours, face (-4, -33): the
  chains arch back, so the tool's head centre (x -9) sits behind the face.
  Codex's fourteen effects came as raw generations with real alpha and a manifest. `tools/art/import_thresh.py
  --raw` sizes them to the kit; three pictures needed more than a scale. The hook's chain is drawn link by link,
  growing with the throw and shrinking with the pull (champion-data section 6: a fixed 48 px chain stuck out
  behind him as it left his hand, and a fixed chain on the hook coming back would overshoot him). The lantern
  is laid along its flight and mirrored top to bottom (art-spec: a projectile flying left is turned upside
  down). The Box's ground was drawn at 1.6:1 and is squeezed toward the game's 2:1, anchored 2 px below the
  drawing's middle (a pentagon's centre lies below its box's).
- **An angel with a sword, wings and a floating glide (Kayle, drawn by Claude, restyled, hand-drawn head
  pasted).** League's Kayle carries every rank's model at once: the level-1 helmet (`level1`), the level-11
  face and white hair (`level11`), three pairs of wings (`wings_up`, `wings_mid`, `wings_bot`) and two swords
  (`sword_*`, `sword_*_combined`). The user took C: the level-11 head, only the upper wings, the combined sword
  (`"hide_submeshes"`; `"submesh_textures"` maps `level11` and the swords and wings to their own maps). Head 3.0,
  legs 0.7, hair 0.5, wings 0.9, sword 0.65, height 32, hovering 3 px; the wings a part of their own
  (`^Wing_Up`, lilac / blue / ice, outlined). The first three faces were rejected ("都不及格 头部细节做的太差");
  drawn square by square on base heads the user took K5 (fair skin, glowing amber eyes, red lip). Her near arm
  held away from her waist left a hole in the armour at game size: `restyle_native.py` `"fill_holes"` (art-spec).
  The move: the graph's `Run` plays `Kayle_Run1` / `Kayle_Run2` (half each) under 490 move speed, a 4.27 s glide
  whose two halves differ (the arms and feet by 5-7 px), leaning, flapping, floating 16 px up and down. The
  user ("要和英雄联盟里面一模一样") took A of three floats shown against League's own: `Kayle_Run1` whole, 16 x
  267 ms, the float kept and only lifted until the lowest frame's feet touch the ground (`"sink": -8`). The
  death: League's tumble back (legs in the air under an upright pasted head read as a head on legs) is left out
  for its second half - kneel, rise, fall forward, lie on her face (`"forward": true` turns the head) - and the
  sword that plants itself upright through her face and the ground is hidden once it leaves her hand.
  Codex's fourteen effects (raw, alpha, a manifest) went in with `tools/art/import_kayle.py --raw`; the heal
  column and the Exalted flames came thinner and taller than asked and are sized by height (42, 40 px). 63
  frames, 42 colours, face (1, -36). In game players found this model "too abstract" (the restyled body a mush
  of gold and grey-green, the wings a few lines): Codex redrew it (`assets/source/kayle/MODEL_REDRAW.md`) - the
  design first, set on the game grid by its own pixel edges and approved; then the 63 frames, one 64x112 canvas
  each (`tools/art/native_frames.py`), delivered raw and tidied by `tools/art/tidy_kayle.py` (art-spec "Frames
  straight from an image model"). 40 px crown to soles, 21 colours, 37% right-neighbour, face (-2, -40) measured
  without the wings, which rise above her head.
- **A scarecrow with a sack head, stilts and a scythe (Fiddlesticks, drawn by Claude, restyled, hand-drawn head
  pasted).** Of three cameras the user took B (yaw 30, pitch 25, not mirrored: the scythe trails behind him
  and the two stilts stand apart); head 2.0, legs 0.75, height 28. The skin's demon arms, lantern and tongue
  are submeshes his base look never shows (`"hide_submeshes"` as a list); the scythe has a map of its own
  (`"submesh_textures": {"Weapon": "Weapon_TX"}`) and is the `weapon` (`^Scythe$`, the blade voted by hue
  onto a rust ramp); the back leg is a part of its own (`^L_Hip$`, darker and outlined apart, so the two
  stilts read). The sack is drawn square by square; of three heads the user took H4: an egg-shaped burlap sack
  leaning back, a tied top with dark purple quills, one red eye and a grin of triangular teeth, pasted on
  League's head joint and kept upright (`"turn": 180`, `PASTED`). His scythe hangs on a root joint of its own
  (`Scythe`) that the clips move along with `Scythe_Snap` under his hand; a frame blended toward the idle lerps
  it on its own, and in Reap's swing the user saw "an arm missing": the scythe had floated off his arm.
  `native_pose.py`'s `"glue": {"joint": "Scythe", "to": "Scythe_Snap"}` puts it back at its place against the
  hand in the pose that weighs more (art-spec "Blends and props on a root joint"). Reap skips the frame where
  League stretches the blade into a smear (400 ms); Terrify's lunge is blended 40-50% toward the idle so the
  big head stays above the ground; the death leaves out League's lift into the air after 2 s and hides the
  scythe once it leaves his hand. The move is `run_base` = `Fiddlesticks_Run` at League's pace (8 frames,
  0.867 s), head like the idle. 65 frames, 29 colours, 36% right-neighbour, face (9, -30).
  Codex's thirteen effects came as raw generations with real alpha and a manifest (`frame_regions`);
  `tools/art/import_fiddlesticks.py --raw` gives each frame the connected drawings lying mostly in its
  rectangle (two crows of the burst crossed into the next cell, and cutting by the rectangles left half a crow
  on one side and a wing tip on the other), mirrors the bolt, the crow and Reap's crescent top to bottom, and
  sizes them to the kit: Crowstorm's mark 90 px wide (radius 45000), its crows round an 84 px ellipse with the
  height squeezed to 0.8 (Codex's cell came square, not 3:2), Reap's crescent 48 px tall - a slash through the
  foes in its 60 px circle - centred on the cast point (a picture turned half round for a cast to the left
  would move an off-centre crescent down).
  In game the user found the scythe's blade, hanging below his soles in the idle, hidden under the health bar,
  and the whole model ugly ("稻草人的模型做的太丑 让codex重做一下吧"): Codex redrew it
  (`assets/source/fiddlesticks/MODEL_PROMPTS.md`). Three designs first - A League's proportions, B chibi, C the
  scythe on the shoulder - and the user had Claude choose: B (the sack a third of his height, the scythe held
  upright behind him, its blade arching over his head: the clearest face and reaper outline, all of it above the
  health bar). The ten strips followed on the reference cells with the same frame timing, nothing under the feet
  line. `tools/art/tidy_fiddlesticks.py` fixes three things on the game pixels: eyes run together into a bar
  (redrawn as the idle's staggered pair), eye green on Reap's scythe pole, and the attack's claw arm stretched out
  of the sack's front at eye height (moved 5 rows down to come out from under the sack). His run drifted 12 px
  about the pivot and the blade is the top of every frame, so `import_native.py` steadies him on his eyes
  (`EYES`, one colour only the eyes use). 65 frames, 15 colours, 25% right-neighbour, face still (9, -30).
- **A fox girl with nine tails (Ahri, drawn by Claude, restyled, head pasted).** Her skin has four submeshes
  (Body, Eyes, Tails, Tail_Large) and two colour maps: the nine tails take `Ahri_Base_Tails_TX_CM`
  (`"submesh_textures": {"Tails": "Tails_TX"}`; on the body's map they came out as red sleeves), and
  `Tail_Large`, the one big tail of her R, is left out (`"hide_submeshes": ["Tail_Large"]`). The tails hang on
  `Tail_Master` under the pelvis, so `--head` does not grow them; at League's size they fanned out wider than
  her body at game size, and the user took proportion A of four (head 2.0, legs 0.8, hair 0.5, tails 0.6 through
  `"chibi": {"scale": {"Tail_Master": 0.6}}`, height 32). They are a part of their own (`"parts"`: the tail
  joints, a lavender-white fur ramp, outlined), the braid and front locks are voted frame by frame
  (`"hair_part"`), and `"crown": 194` measures the height under the fox ears. League lights her skin pink (hue
  340-357 on the thighs), so the skin class wraps the hue (340-40, saturation 0.1-0.42) after the red cloth
  (saturation from 0.42); before that her legs were voted grey. The head is drawn square by square on League's
  traced silhouette at game size (ears dark outside and pink inside over the crown, the blue-black hair mass
  behind, the face on the right) with the face widened to base-hero size - League's own face at head 2.0 is
  four pixels wide - base three-row eyes with amber irises and no mouth (face A of three), and pasted on League's
  head joint (`"dx": -2, "dy": -1`). Spirit Rush's clip flies head first, lying flat (the head joint's tilt
  107-137 degrees); turned a quarter, the pasted head sat on a jumble of limbs, so those frames are blended
  50-65% toward the run's forward lean (`Spell4@t>Run@375:0.65`) and the head stays upright. Orb of Deception's
  mid-air flip (tails over the head) is left out. The move: `Run` plays `run_base` below 451 move speed, a
  sequence of `Run.anm` and then a selector of `Run.anm` (50%), `Run_Var1` and `Run_Var2` (25% each), so the
  run is `Run.anm` at League's 1 s cycle (8 x 125 ms). 55 frames, 32 colours, 37% right-neighbour, 38 px with
  the ears, face (1, -35).
- **A fallen angel in a long gown (Morgana, drawn by Codex from the start).** The camera mirrored, yaw 20, pitch
  25 (League's idle stands turned, so the gown's train lies behind her); head 2.4, height 37; the open wings and
  the flower are submeshes her base look hides at first (`"hide_submeshes"`). Codex's first three designs came as
  raw drafts (a 128-square picture stretched to 1254 px); the user took B (art-spec "A design draft bigger than
  the game") and it was animated, then Morgana was redesigned from a splash the user gave (art-spec "A redesign
  from the user's picture"): the eight animations drawn again on design A, raw, and tidied by
  `tools/art/tidy_morgana.py` (art-spec "Whole raw sheets"). The idle is the design six times, breathing on a seam
  five rows over the gown's hem; the move is steadied on her eyes (`EYES`). 50 frames, 26 colours, 45 px with the
  horns, 40% right-neighbour, face (-2, -41) at the crown between the horns. Codex's eleven effects: `tools/art/import_morgana.py
  --raw`, anchors measured on the drawings (art-spec "Effect anchors"); the shackles play the 2 s root in one
  Animation, the pool its 4 s, the snap the chains breaking round the waist and then the stun sigil 40 px up.
- **A girl locked in a pillory (Briar, drawn by Codex from the user's picture).** The picture was an earlier Codex
  image on an irregular 7-px grid (59 x 71 squares): cut to game size by rows and columns it lost the hair, the eyes
  and the gold trim, and Codex's own area-averaged 46-row copy blurred the face, so Codex redrew it about 76 squares
  tall (1.7x the game size), A in the picture's proportions and B chibi (art-spec "A redesign from the user's
  picture"). Claude cut it to 46 rows from the gem to the soles by deleting whole rows and columns, kept one outline,
  added a lash row, made both eyes 2x2 on one row in an ice-white used nowhere else and redrew three mouths on the
  face's middle line (the cut had dropped Codex's); the user took B with mouth 3. The camera yaw 45, pitch 25, head
  2.3, legs 0.8, hair 0.6, height 35; the move is League's `Run1` (8 x 125 ms). Codex pasted the head into every
  strip frame as its whole rectangle and left a window round it, which `tools/art/tidy_briar.py` closes (art-spec
  "A pasted head's rectangle cuts a window"). The pillory's gem is the top of every frame, so the idle and the move
  are steadied on her eyes (`EYES`). 61 frames, 23 colours, 46 px with the gem, 35% right-neighbour, face (-3, -34)
  at the crown (`tfm2_ase.py face` suggests the gem). Codex's fifteen effects: `tools/art/import_briar.py --raw`,
  anchors measured on the drawings; the frenzy's ground line, a flat 15x2 bar at 44 px, is cut (it read as a second
  health bar).
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
  Names that live only in the in-game tooltips (Kayle's rank names 狂熱 / 轉生 / 熾烈 / 超然, 열광 / 비상 /
  작열 / 승천, ゼレス / アライズン / アフレイム / トランセンデント) are not in Data Dragon or in CommunityDragon's
  champion JSON: read the locale's whole string table from CommunityDragon
  (`raw.communitydragon.org/latest/game/<zh_tw|ko_kr|ja_jp>/data/menu/en_us/lol.stringtable`, 21-24 MB, RST v5)
  at the key the local en_US table gives for the tooltip.
- Riot allows non-commercial fan content; keep extracted audio out of public repos anyway
  (re-extract with the tool) and add the disclaimer (League of Legends (c) Riot Games).
