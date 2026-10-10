# .data_champion reference

Schema, units, enums and the effect catalogue, compiled from the 8 base `.data_champion` files,
the base `champion_info` sheet (68 champions), 52 champions in two large Workshop packs, and
strings in the game binary. Anything marked *(inferred)* was deduced from usage, not documented.

Contents
1. Top-level fields
2. Units and balance ranges
3. Actions (attack / skill / skill2 / ult)
4. Effect catalogue
5. buff_state
6. View bindings (how things become visible)
7. Patterns that work (copy these)
8. Gotchas
9. Checking a fact against the engine

## 1. Top-level fields

| Field | Notes |
|---|---|
| `id` | Unique, namespaced (`league_garen`). Also the key for text and champion_view. |
| `category` | `Melee` \| `Range` \| `Magician` \| `Util` \| `Assassin` (drives UI filter + AI role) |
| `tags` | Free strings used in packs: `AD` `AP` `Melee` `Range` `Tank` `CC` `Magic` `Heal` `Shield` `Dot` |
| `sprite` | `asset/<mod_id>/champions/<hero>` (no extension) |
| `anim_prefix` | `""` in every pack |
| `skill_icons` | 3 paths: skill, skill2, ult (64x64 PNG) - or `skill_icon: {source, tags}` atlas |
| `stat` / `growth` | 9 keys each: `attack magic_power hp defence magic_resistance move_speed hp_regen stack crit_chance` |
| `attack` `skill` `skill2` `ult` | the four actions (section 3) |
| `view_projectiles` `view_effects` `view_buffs` | bindings from effect names to animations (section 6) |

**Named native passives (game 0.6.0+).** `passive` (from spawn), `passive_skill2` (once skill2 is learned) and
`passive_ult` (once the ult is) each take `{"passive_ref": "<name>", "params": {...}}`: one of the base game's own
passives run by its native code - `ogre` (`hit_hp`), `dancer` (`vamp`), `ghost` (`heal`, `add_attack`,
`add_attack_speed`), `circus_blade` (`charge_count`), `gunner` (`move_speed_up`, `move_speed_up_duration`), `hunter`
(`recast_duration`, `kill_extend_count`), `berserker` (`cooltime_reduction`, `max_cooltime_reduction`),
`poison_dart_hunter` (`add_move_speed`, `range`), `swordman`, `vampire` - or a name a native mod registered
(`my_mod:frenzy`). Every param is required and a non-negative integer: a missing one, or an unknown name, makes the
game log one warning and skip the passive (the champion still loads). Stacks live on the player and survive death;
`stack_skill_index` (0 skill, 1 skill2, 2 ult) picks the icon that shows the stack counter. Source: the official
schema (teamsamoyed/TeamfightManager2Mod, docs/data-champion-schema/passives.md); the classic SDK's
`DataChampionInfo` (0.5.1, the last one with the engine, section 9) has none of these fields, so the simulator
cannot run them and no hero of this pack uses them yet. There is no "on spawn" hook, so a passive of our own is
still built with buffs (section 7); a permanent one goes on at the first action (league_amumu's Tantrum
armour: `SwitchByBuff` on itself, then `AddCasterBuff` with `"duration": "Permanent"`).

## 2. Units and balance ranges

- **Time: 60 ticks = 1 second.** (Aatrox's 600-tick buff is described in-game as 10.0 s.)
  `duration`, `cooltime`, `start_timing`, buff `tick`, `Stun.duration`, `Delayed.tick` are ticks.
- **Distance:** melee attack range 23000-30000, ranged 40000-80000, typical AoE radius
  25000-40000, projectile speed 3000-7000. Roughly 1000 units per sprite pixel *(inferred)*.
- **Ratios are percentages:** `attack_ratio: 120` = 120% AD.
- `move_speed` 900-1200; `*_mult` buff fields are percentages (`move_speed_mult: -30` = 30% slow).

Base game ranges (median [IQR] (min-max), 68 champions) - rebalance ported heroes into these:

| Category (n) | attack | growth | magic_power | growth | hp | growth | defence | mr | move | attack range | atk cooltime |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Melee (20) | 95 [80-100] | 19 | 0 | 0 | 1000 [950-1100] | 100 | 30 [30-40] | 25 | 1000 | 25000 | 65 |
| Range (11) | 100 | 20 | 0 | 0 | 900 | 90 | 20 | 15 | 900 | 60000 [50k-60k] | 60 |
| Magician (15) | 80 | 6 | 40 | 20 | 900 | 100 | 20 | 20 | 900 | 60000 | 90 |
| Assassin (10) | 120 | 30 | 0 | 0 | 900 | 80 | 25 | 15 | 1100 | 23000 | 50 |
| Util (12) | 80 | 6 | 30 | 15 | 900 | 100 | 20 | 20 | 1000 | 60000 [25k-60k] | 90 |

Growth for defence is ~7-9, magic_resistance ~3-5, move_speed ~9-14.

Cooldowns (ticks, median [IQR]): skill 240-420, skill2 300-480, ult 2400-3600 (almost always
3000). Attack `duration` ~20-30 with `start_timing` ~13-18.

The 11 base tanks (Melee with the `Tank` tag) sit at attack 80, magic power 0, hp 1100, defence 40,
magic resistance 30, attack range 25000, attack cooldown 70, growth attack 6 / hp 120 / defence 10 /
magic resistance 5; their stuns last 60 ticks, some every 180-240.

**What else is on the map** (`asset/base/setting/game_setting`): the full mode has lanes with
minion waves (melee 400 hp, ranged 250 hp, +20-30 per level), jungle camps (300-700 hp, +100-150),
an epic monster (10000 hp, +1500, 150 defence and magic resistance) and the serpent (5000 hp, +1000),
towers (2000 hp) and levels (`need_exp`, 12 levels). `champion_radius` is 10000. So `EnemyWithoutTower`
also means minions and monsters: a non-penetrating skillshot on it stops on the first minion, and a
%-max-health effect on it melts the epic monster (league_amumu keeps both to `EnemyChampion`).

## 3. Actions

```json
"skill": {
  "action_name": "skill",            // sprite tag played for this action (must exist!)
  "description": "#asset/base/text/champion?description.<id>.skill",
  "duration": 20,                    // ticks the caster is busy
  "cooltime": 300,                   // ticks
  "cooltime_use_count": 3,           // optional: charges / recasts (base Nightmare)
  "start_timing": 8,                 // tick at which `effect` fires (<= duration)
  "cancelable": false,
  "range": 50000,                    // AI casts when a valid target is within range
  "casting_type": "Direction",       // Targeting | Direction | Position | None
  "casting_target": "EnemyWithoutTower",
  "attack_type": "Skill",            // BaseAttack for `attack`, Skill otherwise
  "can_use_with_move": true,         // optional
  "effect": { ... }                  // effect tree (section 4)
}
```

- Levels gate the slots *(read from the SDK's game_core `Entity::run`, league_kayle)*: the attack and `skill`
  from level 1, `skill2` from level 3, `ult` from level 5.
- A `range` caster buff (attack range) also stretches the distance at which the AI starts attacking
  *(SDK simulation, league_kayle Arisen: melee at levels 1-4, she fought from 52500 after it)*.
- `casting_target`: `Enemy`, `EnemyWithoutTower`, `EnemyChampion`, `EnemyChampionInCC`,
  `EnemyChampionRecentlyAttacked`, `AllyOnlySelf`, `AllyChampion`, `AllyNotSelf`,
  `AllyChampionInCC`, `BothWithoutTower`, `BothChampion` (the engine also has `Ally`, `Both`, `None`).
  `EnemyChampionRecentlyAttacked` is an enemy champion that the caster's *team* damaged recently
  (a per-team timer on the target, `CastingTarget::check`), not one the caster hit itself. It is the best stand-in
  for "a wounded champion" that an execute can have (nothing reads current health): league_darius R on
  `EnemyChampion` opened fights on champions at full health (players: 「现在AI会满血释放大招」); on
  `EnemyChampionRecentlyAttacked` the targets at 75% health or more went from 10 of 53 casts to 3 of 52 and those at
  30% or less from 11 to 20, 4.3-4.4 casts a game either way (12 simulated games, 2026-10-04). Gating it on his own
  hits instead (league_riven's armed ult, landed by the attack that brings Noxian Might, or the fourth or third hit
  in 5 s) cut the casts to 2.3-2.5 a game and left the targets' health after the blow where it was (35-45% against 39%).
  `EnemyChampionInCC` / `AllyChampionInCC` is a champion carrying one of six crowd-control states
  *(read from the SDK's game_core: `CastingTarget::check` tests the target's CC list against mask
  0x347)*: airborne (`Airborne`), stun, root (`Bind`), forced movement (`Knockback`, `Pull`, `Grab`),
  fear and charm. Disarm (`BlockAttack`), silence (`BlockSkill`), `BlockMoveSkill`, taunt and slows
  (slows are buffs) do not count, and no target narrows it to knock-ups only: league_yasuo's R, cast on
  `EnemyChampionInCC`, also fires on stunned or rooted champions. No base champion's data uses it.
  As a projectile's `applied_target` it is tested when the projectile hits (league_fiddlesticks Q,
  section 7).
- **An empty branch does not hold every slot** *(SDK simulation, league_leesin, 2026-10-02)*: league_caitlyn W
  (`SwitchByBuff w_hold`, empty for the buff) kept its charges, but league_leesin's E (`None` on
  `EnemyWithoutTower`) behind a flag went out empty in fights and on camps, and its ult (`Targeting EnemyChampion`)
  right after every combo that set the flag - each cast also starting the slot's real cooldown. Do not hold a slot
  with a flag; let the slot play the combo (section 7, "Combos the slots play").
- **Damaging basic abilities go on `EnemyWithoutTower`** *(reported by players; measured in a 5v5
  simulation on the SDK)*. The AI only casts an action while a unit matching `casting_target` is
  within `range`, so a skill on `EnemyChampion` is never used on minions or jungle monsters: the
  first pack heroes had it everywhere, league_leesin cleared camps with auto-attacks (10 simulated
  minutes: 14 Q and 3 E casts; 48 and 26 on `EnemyWithoutTower`, and he took less damage) and
  Garen never spun on a wave. Keep `EnemyChampion` for ults and for abilities wasted on anything
  else (league_darius E pull, league_amumu Q engage). `EnemyWithoutTower` includes the epic
  monster (see section 2).
- **Which ally gets an ally skill** *(read from the mod SDK's compiled `game_core`, not yet seen
  in game)*: `AllyNotSelf` is an allied champion other than the caster (no minions), `AllyChampion`
  includes the caster, `Ally` is any allied unit (`CastingTarget::check`). The battle AI makes one
  candidate per valid ally for skill, skill2 and ult (`utils::battle_ally_action`) and scores it;
  a heal is worth `min(heal, target max HP - HP)` on that target (`Effect::expected_heal_target`),
  so heals should go to the most injured ally and a full-health ally is worth 0. No casting target
  means "lowest health": base Priest's ult finds that ally in hard-coded logic
  (`lowest_hp_ally_in_range`). Heal, RangeEffect, Combine, Delayed, WithSelf and the projectiles
  all report their expected heal, so a heal nested in them still counts.
  As a zone's `applied_target` `AllyNotSelf` is wider: league_sona's first Song of Celerity aura
  (`ApplyInProjectile` on `AllyNotSelf`) hastened her side's minions and towers too (the simulation's buff
  events, 2026-10-02); on `AllyChampion` it reached champions only, her as well.
  **In the simulation the health does not steer it** *(SDK simulation and disassembly, league_kayle,
  2026-09-29)*: `battle_ally_action` is called only by the legacy poke / hunt sub-plans (serpent, epic
  monster); the battle sub-plan's `base_battle_action` checks the casting target and range and scores
  damage (`expected_damage_target`), not heals, and `lowest_hp_ally_in_range` belongs to base Priest's
  native ult runner. league_soraka W (`Targeting AllyNotSelf`, a heal) went out every 4 s, often on
  allies at full health (archer 1260/1260, pyromancer 1500/1500) while others were hurt; a probe ult
  on `AllyChampion` (invulnerability, with or without a 150 or 2000 heal) was cast on cooldown, the
  receiver at 84-94% health on average, the most injured champion in reach skipped (a ninja at 48%
  while a 74% pyromancer got it). No effect a mod can use reads a unit's current health either
  (`Heal`, the attack effects and the buff fields know only maximum health; base-only `Native` and
  `AddStatScaledBuff` aside), so "save the one about to die" cannot be written - see section 7 "An ult
  that waits for danger" for what can.
- **A shield is worth its full amount on anyone** *(read from the SDK's game_core,
  `ShieldEffect::expected_shield`: the amount plus its ratio parts, nothing about the target; measured
  in the SDK simulation for league_janna E)*. Unlike a heal, a shield's score ignores the target's
  health and whether any enemy is near, so a shield on an ally target goes out whenever it is ready:
  league_janna's first E (`Targeting AllyChampion`, 7 s) was cast on cooldown, mostly on herself, often
  at full health with no enemy champion within 100000; on `AllyNotSelf` with a 5 s cooldown it went
  out 46 times in 10 minutes, most of them out of any fight, and her team did worse (kill difference
  -1.32) than with the same shield cast on an enemy champion and handed to an ally from there (+0.29,
  section 7 "Shield the ally beside her, only in a fight").
- Self-buffs that should fire "in combat" work best as `casting_type: None` +
  `casting_target: EnemyChampion` + a `range` (cast when an enemy champion is that close) - this
  is how Nocturne's shroud is wired. `AllyOnlySelf` + range 0 also exists (Aatrox ult).
- **A heal on the caster is cast whenever it is ready, not when he is hurt** *(measured in the SDK
  simulation for league_masteryi's Meditate, 4 ten-minute games per variant)*. On `AllyOnlySelf`
  (`Targeting` or `None`, the same result) and on `AllyChampion` with range 0 the skill went off
  about every time its cooldown ended, at 76-94% health on average and often at full health; the
  missing-health score above did not hold it back. On `EnemyWithoutTower` within melee range it goes
  off as a fight starts. So give a self-heal something worth having at full health too:
  league_masteryi meditates for 0.75 s (40% less damage taken, a heal over 2 s) and then gets Wuju
  Style. (Until 0.15.0 that heal sat in a `WithSelf` of a `None` action and never ran, section 4.)
- `action_name` may be any tag: `ult_cast`, `skill2_dash`... Base uses this heavily.
- `can_use_with_move` lets the unit cast without stopping. No base skill uses it (LoL Reborn
  does), and it does not let the unit walk during a `CasterAnimation`.
- **Attack speed shortens `start_timing`, not `Delayed`** *(measured in the SDK simulation)*. A basic
  attack with `start_timing: 12` fired its effect 13 ticks after the action began at 100% attack speed,
  7 at 200% and 4 at 400% (the action event reports the speed as `speed_mult`); a `Delayed {tick: 9}`
  inside it stayed 9 ticks at every speed. An attack that must choose its animation first (league_jinx:
  minigun or rockets) branches at `start_timing: 1` and fires its projectile from a short `Delayed`; at
  200% attack speed that lands about 3 ticks after the frame drawn for it.
- `patch_type_name` only appears in base data (patch notes); skip it.

## 4. Effect catalogue

Every effect is `{"type": "<Type>", ...fields}`. Counts = uses across base + 52 pack champions.

**Flow**
| Type | Fields | Meaning |
|---|---|---|
| Combine | effects[] | run all, in order |
| Delayed | tick, effects[] | run after `tick` |
| WithSelf | effects[] | the caster, **and again the action's target** when that is another unit; nobody when the action has no unit target (below) |
| SwitchByBuff | buff_name, effect_buff, effect_none | branch on whether the **caster** has the buff |
| SwitchByLevel3 | effect_start, effect_level3 | `effect_level3` when the **caster** is level 3 or higher, `effect_start` below - the only effect that reads a level *(read from the SDK's game_core: the entity's level field, written by `add_exp`; league_kayle)* |
| RandomTarget | range, casting_target, from_projectile, effects[] | pick a random valid unit in range, apply effects to it |
| RangeEffect | shape, target, apply_type:"AroundCaster", effects[] | instant area around the caster |

**Damage and sustain**
| Type | Fields | Meaning |
|---|---|---|
| Attack | damage, attack_ratio, hp_ratio, target_hp_ratio, attack_effect_type:"Target" | physical: damage + ratio% AD (+% max-HP parts) |
| ApAttack | damage, attack_ratio, hp_ratio, can_crit | magic: damage + attack_ratio% **AP** |
| FixedAttack | damage, attack_ratio, hp_ratio, target_hp_ratio | true damage: damage + ratio% AD + hp_ratio% of the caster's and target_hp_ratio% of the target's **max** health |
| Heal | amount, attack_ratio, ap_ratio, heal_type: Caster\|Ally\|Any\|AllyAll | heal (`Caster` heals the caster even inside a projectile that hit an enemy; `Ally` the allied target). No field scales with the target's missing health |
| Shield | amount, attack_ratio, ap_ratio, tick | shield for `tick`; separate shields add up (league_yone W) |
| AddCasted | casted_type: Fire\|Poison\|Bleed\|Heal, duration, period, effects[] | damage-over-time: run effects every `period`; every cast adds another instance (see below) |

Defaults *(read from the SDK's game_core)*: `attack_ratio` of Attack, ApAttack and FixedAttack is
**100 when left out** (Heal and Shield default to 0), so always write it, even as 0. No attack
effect has a missing-health field: `target_hp_ratio` is a share of the target's maximum health.
A key the effect does not have is skipped without a word: league_garen's Q shield wrote `hp_ratio:
6` (a Shield has none) and shielded 60 instead of the 60 + 6% max health its text promised, until
it became 60 + 50% AD. `lint_mod.py` warns about both (unknown fields, a missing `attack_ratio`).
`ApAttack` has no `target_hp_ratio`, so "% of the target's max health as magic damage" (Amumu's
Despair) cannot be magic: league_amumu deals that part as `FixedAttack` (true damage). All the ratio
fields are whole percents (`usize` in the SDK; `0.5` is a parse error), so a pulse every second can
take no less than 1% of max health.
`hp_ratio` on the three attack effects is a share of the **caster's** maximum health *(measured in the
SDK simulation for league_malphite E: 60 + 50% of 75 ability power + 5% of his 1460 health = 170, and the
fighter it hit took 128 after 32 magic resistance)*. No effect reads armour, so League's armour ratios
(Malphite's Ground Slam, Thunderclap) become `hp_ratio`, the tank stat the data can read, as the base
ogre's skill and LoL Reborn's Galio, Sion and K'Sante do. A `Shield` has no `hp_ratio`: a shield of "10%
of max health" is a flat amount plus `ap_ratio` (league_malphite's Granite Shield, section 7).

`AddCasted` never refreshes or replaces: `AddCastedEffect::apply` pushes a new entry on the target's
list of casted effects each time, so repeated hits stack, each with its own timer, and nothing caps
the count. `Bleed` is the base Inquisitor's bleed (league_darius uses it for Hemorrhage).

`attack_effect_type` on the three attack effects: `Target` (every pack writes it) hits the
effect's own target with no team check, so a `FixedAttack` given to the caster alone (a `RangeEffect` on
`AllyOnlySelf`, below) damages the caster;
the engine's other kinds are `EnemyTarget` (skips the caster's team) and `EnemyAll {..}`.
`FixedAttack` with only `target_hp_ratio` has an expected damage of 0 for the AI (it is
estimated from the caster's stats), which keeps a health cost out of the skill's score.

**`WithSelf` is not "the caster only"** *(read from the SDK's game_core, `WithSelfEffect::apply`, and
measured in the SDK simulation for league_janna, 2026-09-28)*. When the action's target is a unit other
than the caster, it applies its effects to the caster and then **again to that target**; when the target
is the caster, or the action has no unit target (a `None`, `Direction` or `Position` cast), it applies them
once, to that target - so to nobody. A `WithSelf {FixedAttack 77}` in a basic attack hit the attacker 30
times and the enemy champion she attacked 7 times; the same wrapper in a `None` skill hit no one. Every self
effect written this way misfired until 0.15.0: league_soraka W's 6% health cost also hit the ally she healed
(a fighter lost 89 = 6% of 1490), her Q's Rejuvenation hung a second heal over time on the enemy champion hit,
league_annie W's Molten Shield also shielded the enemy it was cast on, league_yasuo's Flow shielded the enemy
he attacked or dashed through (and nothing when Q set it off), and league_masteryi's Meditate never healed.
For the caster alone use `RangeEffect {shape: {Circle: {radius: 1000}}, target: AllyOnlySelf, apply_type:
AroundCaster, effects: [...]}`: it reached the caster only, in `Targeting` and `None` actions and in a
projectile's `applied_effects` alike. `lint_mod.py` warns about a `WithSelf` around an effect on a unit.
Wrappers that only touch the caster's own buffs (the kill checks of league_jinx and league_missfortune,
league_jinx's trap lock, league_annie's Pyromania, league_teemo's trap flags) run twice with the same result.

**Critical strikes follow the action's `attack_type`** *(read from the SDK's game_core,
`apply_attack_inner`)*. In an action with `attack_type: BaseAttack`, every `Attack` (in projectiles
too) rolls a crit: chance = the `crit_chance` stat plus buffs, capped at 100, and a crit deals
exactly **2x**. In a `Skill` action an `Attack` never crits (`AttackEffect` passes no skill-crit flag);
only `ApAttack` with `can_crit: true` can. The type also picks the target's reduction:
`base_attack_damaged_reduce` for `BaseAttack`, `skill_damaged_reduce` for `Skill`. Setting a skill's
action to `BaseAttack` is how "treated as a basic attack" is built (base swordman's skill does it;
league_yasuo's Q crits that way). No base champion has crit chance (items give 10-25%), a crit's
damage cannot be changed, the chance can only be added to (no multiplier), and the stats panel does
not show it, so write it in the text. `defence_penetration` is a percent: the target's armour counts
as armour x (100 - penetration) / 100 (`utils::get_damage`).

**True damage that scales with ability power** *(measured in the SDK simulation for league_ahri Q,
2026-09-29)*. `FixedAttack` reads the caster's attack damage and health, never ability power, so a
spell's true damage in AP terms is an `ApAttack` that ignores magic resistance: put `AddCasterBuff
{duration: 1 tick, magic_resistance_penetration: 100}` right before it in the same applied effects. The
buff counts for the hit in the tick it is added (the same 55 + 45% AP dealt 140 through a lightning
mage's magic resistance and 190 with the buff), and it is gone the next tick; other damage the caster
deals in that very tick gets it too. Reductions that are not armour or magic resistance
(`damaged_reduce`, `skill_damaged_reduce`, shields) still apply, as they do to `FixedAttack`.

No effect and no buff field blocks, reflects or destroys a projectile (a wall like Yasuo W or Braum E
cannot exist); `ShrinkingBarrier` is a closing ring that hits units at its edge.

**Buffs** - `AddBuff {buff_state}` (on target), `AddCasterBuff {buff_state, only_to_enemy}`
(on caster), `RemoveCasterBuff {name}`. See section 5.

**Crowd control / states** (durations in ticks)
`Stun {duration}`, `Airborne {duration}`, `Bind {duration}` (root), `Taunt {duration}`,
`Banish {duration, end_effect_name?, lock_effect_name?}` (removed from play),
`Charm {tick}`, `Fear {tick}`, `Knockback {speed, tick}`, `Pull {speed, tick}`, `Grab {speed, tick}`,
`BlockAttack {tick}` (disarm), `BlockSkill {tick}` (silence), `BlockMoveSkill {tick}` (no dashes),
`Invisible {tick}` (Nocturne ult applies it to allies), `CasterInvisible {tick}` (base Nightmare).

**Charm walks the target to the caster** *(measured in the SDK simulation for league_ahri E,
2026-09-29)*. For `tick` ticks the charmed unit walks straight toward the caster at its own move speed
(a lightning mage 79000 units away came about 460 units closer every tick, and turned away the tick the
charm ended), then goes back to what it was doing. It is crowd control for `EnemyChampionInCC`
(league_yasuo's R fires on it, section 3). The simulation's frames carry no charm event of their own
(`Stun` and `Airborne` have one), so a logger sees it only in the target's movement.

**Invisible is not untargetable; Banish is** *(read from the SDK's game_core and measured in the
5v5 simulation for league_teemo and league_masteryi)*. `Invisible` and `CasterInvisible` set the same
timer on the unit (the longer one wins; `CasterInvisible` also sends the client an "invisibled"
event). It only takes the unit out of the enemy team's vision (`World::build_visible_map`), and
enemies next to it see it again. Teemo's W hides him as he runs off (90 ticks): the `EntityInvisibled`
event turns on 4 ticks into the action and off exactly `tick` later, his attacks meanwhile do not end
it, and enemy champions stopped choosing him as a target - two of about twenty enemy actions in the
windows still did, both right at the start. Master Yi blinks into the enemy team instead: with 300
ticks of `CasterInvisible` after each blink, enemy champions still started about 20 attacks and skills
on him per game inside those windows. `Banish` sets the unit's block-target timer as well
(`EntityCanTarget { can_target: false }`), and `CastingTarget::check` refuses a target that has one,
so nobody can pick it; it also adds a CC state and makes it invisible. The Touhou pack banishes its
caster this way (Koishi's ult, `RangeEffect` on `AllyOnlySelf`; a `WithSelf` would banish the action's
target as well, section 4). While the
caster is banished its own `RandomTarget` finds no unit at all, but effects on the action's target,
`Teleport` and queued `Delayed` effects still run.

**A banished unit gives its team no vision** *(seen in game by the user and measured in the 5v5
simulation for league_masteryi)*. The client hides every unit its team does not see (the
`EntityIsVisible { is_visible: [team 0, team 1] }` events), and while a unit is banished it stops
counting for its team's vision. Master Yi, banishing himself between Alpha Strike's blinks, made the
jungle monsters and enemy champions around him vanish from the screen at every blink whenever no ally
stood near: 1053 such drops inside his Q in 8 simulated games, 280 once the banish was gone (the fog's
ordinary comings and goings, the same as with invisibility alone). Invisibility does not do this. The
engine also has a plain `BlockTargetEffect` (untargetable, nothing else), but the data format does
not reach it (`sdk_probe` lists the accepted effect types) and `Native` needs game code, so a mod
hero cannot be untargetable and keep his vision - see "Untargetable window".

What the game shows by itself: an `AddCasted` of `casted_type: Poison` puts a `poison` status icon on
the target, `BlockAttack` a `buff_disable` one, a `move_speed_mult` buff `movement+buff` /
`movement+debuff` and an `attack_speed_mult` buff `attack_speed+buff` (the `status_icons` of the
`EntityInfo` events), so a poison or a blind needs no effect of its own to be readable.
Every `casted_type` has its icon, and those four are all the engine accepts (an unknown variant lists
`Bleed`, `Poison`, `Fire`, `Heal`): `Bleed` shows `bleeding`, `Fire` `burn`, `Heal` `heal` *(measured in
the SDK simulation for league_missfortune)*. So an `AddCasted` kept on a target as a hidden marker shows
the wrong icon for as long as it lasts (a 75-tick "is my last target alive" mark put a heal icon over
every enemy she shot); a 3-tick check (the kill trigger in section 7) only blinks one.

**Pull vs Grab** *(read from the SDK's game_core, `Entity::pull` / `Entity::grab`)*. Both move the
target in a straight line at `speed` units per tick for their duration (tenacity shortens it) and
are blocked by `cc_immune`. `Pull {speed, tick}` heads for the caster, or for the projectile's
position when it runs in a projectile's `applied_effects` (the Touhou Patchouli vortex), and does not
stop there: a target closer than speed x tick is pulled through and out the other side. `Grab
{speed, tick?}` always heads for the caster; with `tick` left out its duration is distance / speed,
so the target stops at the caster wherever it started (league_darius E). A `Stun` and a `Grab` from the
same hit both hold: the stunned target is dragged in at 1500 units a tick until the bodies touch (about
10000 between the centres); the drag heads for wherever the caster is, but its length was fixed when it
started, so a caster who walks off meanwhile leaves the target short of him (20000 in one game) *(measured
for league_thresh Q in the SDK simulation, 2026-09-29)*.

**Movement**
| Type | Fields | Meaning |
|---|---|---|
| MoveTo | speed, range, end_effects[] | dash in cast direction/position, then end_effects |
| MoveToTarget | speed, range, end_effects[] | dash onto the target, then end_effects |
| MoveBack | speed, tick | hop backwards: in a `Targeting` cast straight away from the target, speed x tick units; in a `Direction` cast nothing moves *(measured, league_ezreal E)* |
| RushTime | speed, tick, range, casting_target, penetrate, applied_effects[] | charge for `tick`, hitting units passed |
| RushMoveToBack | speed, applied_effects[] | dash through the target to 15000 units behind it; applied_effects run on it when the caster reaches it (not behind it) |
| DirTeleport | moved | blink `moved` units in the cast direction; only in `Direction` casts. `moved` is an unsigned 64-bit field: a negative value fails to parse and breaks the whole kit |
| Teleport | - | put the caster on the target's (or the cast point's) position |

*(read from the SDK's game_core)* `RushMoveToBack` aims at a point 15000 units (a fixed value) past
the target on the line from the caster, clamped to the map, and schedules `applied_effects` (plain
effects, no `casting_type` wrappers) on the target: a dash *through* an enemy (LoL Reborn Fizz Q,
Touhou Sakuya, league_yasuo E), where `MoveToTarget` stops on it. The point is fixed where the target
stood when the rush started, and `applied_effects` fire when the caster first touches the target,
still about 13000 short of its centre, not once he is behind it *(measured in the SDK simulation with a
marker effect, league_leesin R, 2026-09-29)*. `Teleport` copies
the target unit's coordinates (`Targeting`) or the cast point (`Position`) onto the caster and does
nothing for `Direction`. `Airborne` on a unit that is already airborne keeps the longer of the two
remaining times; every CC's duration is cut by the target's `toughness` (x (100 - toughness) / 100),
and airborne also cancels the target's dash.
`MoveTo` in a `Targeting` action dashes all the way to where the target stood when the dash began: its
`range` does not cap the distance *(measured in the SDK simulation for league_ekko E: speed 3000, range
15000, dashes of 12500 to 54000 units that each ended on the target's spot)*.

**Projectiles and zones** (all take `name` -> bound in `view_projectiles`; `applied_effects` items are `{"casting_type": "Targeting", "effect": {...}}`)
| Type | Extra fields | Meaning |
|---|---|---|
| TargetProjectile | speed, y_offset, applied_target | homing on the target |
| AutoTargetProjectile | speed, range | seeks targets itself |
| TargetSplashProjectile | speed, range, y_offset | homing, then splash |
| LinearProjectile | speed, range, shape, penetrate, end_effects, y_offset | skillshot |
| BackToCasterLinearProjectile | speed, range, shape, penetrate, end_effects | boomerang |
| ParabolicProjectile | travel_time, range, shape, range_effect_name, end_effects | lobbed to a spot |
| LineRangeProjectile | width, length, delay, apply | line/rectangle: hits once `apply - 1` ticks after it appears, gone after `delay - 1` |
| RangeProjectile | shape, delay, apply | circle at the target spot, timed like the line; it has no `end_effects` |
| RangePeriodProjectile | shape, tick, period, first_delay, end_effects | persistent zone ticking every `period` |
| ApplyInProjectile | shape, tick, follow_caster | aura / zone that can follow the caster |

`applied_target`: `Enemy`, `EnemyWithoutTower`, `EnemyChampion`, `EnemyChampionInCC`, `Ally`,
`AllyChampion`. RangeEffect `target` also accepts `AllyOnlySelf`, `AllyNotSelf`.

How they behave *(measured in the SDK simulation for league_jinx, 3-12 ten-minute games each)*:
- A projectile placed in another projectile's `applied_effects` is never spawned (a `RangeProjectile`
  there: 116 hits, no zone). A `TargetProjectile` inside a `Delayed` there does fly, from the caster at the unit
  hit (league_morgana R chains nine of them, section 7). `end_effects` of `LinearProjectile` and `ParabolicProjectile` are plain
  effects run once where the projectile stopped or landed, so zones, `ViewEffect`s and further
  projectiles can start there (LoL Reborn Jinx's rocket splash, league_ashe R).
- `RangePeriodProjectile`'s `end_effects` are applied effects (`{casting_type, effect}`), run on each
  unit in the area when it ends (LoL Reborn Viktor stuns with them), not once at its position.
- `RangeProjectile` and `LineRangeProjectile` hit once and are gone: `apply` is when, `delay` is how long
  they last *(measured for league_leona, 2026-09-28: a probe `ViewEffect` in `applied_effects`, a radius
  large enough that nobody walks out)*. Counting the tick it appears as 0, the hit comes at `apply - 1` and
  the projectile is removed at `delay - 1` (delay 38: apply 1 hit at 0, apply 20 at 19, apply 38 at 37 on
  the removal tick; apply 39 and apply 270 never hit). `delay: 1, apply: 1` hits the tick it appears. It is
  not a lasting trap. Until then this file read `delay` as the moment: league_soraka's star (delay 24,
  apply 10) hit 0.15 s after it appeared while its picture lands at 0.4 s (now delay 35, apply 25: the hit
  on the landing frame, gone with the 570 ms picture); league_lux R's damage line and league_ashe W had
  apply 3 and hit at tick 2, before the beam and the arrows (both now timed by `apply`, section 7).
- `RangeProjectile` has no `end_effects` (game_core reads name, delay, apply, shape, applied_target and
  applied_effects; `lint_mod.py` now knows the fields of every effect type from the SDK). league_soraka's
  Equinox field sat in the star's `end_effects` from her first version and never appeared; it now starts
  from a `Delayed {tick: 24}` in the same cast (a `Position` cast's effects keep the cast point).
- `TargetSplashProjectile` homes on its target and hits every unit within `range` of itself on the way,
  the target included; with `range` 20000 at speed 4500 the target is hit about 5 ticks before the
  projectile reaches it.
- `RandomTarget {from_projectile: true}` measures its `range` from the projectile (the hit point)
  instead of the caster. With `casting_target: AllyOnlySelf` in a zone's `applied_effects` it asks "is the
  caster inside this zone": it finds the caster only while he stands within `range` (plus his radius) of the
  zone's centre, whichever allied unit set the application off *(measured for league_ekko W, every tick of a
  `period: 1` zone on `AllyChampion`)*. In a `TargetProjectile`'s `applied_effects` it asks "is the caster
  within `range` of the unit it hit" (both bodies add about 18000); in a plain `Delayed` on a unit, with no
  projectile, it finds nobody *(measured for league_morgana R, 2026-09-29)*.
- `end_effects` of a `LinearProjectile` or `ParabolicProjectile` run on a position (the stop or landing
  point), and a `Delayed` among them keeps it, like a `Position` cast: a `ViewEffect` there plays on that
  point, a zone or another projectile starts there, and a `Teleport` puts the caster there *(measured for
  league_ekko)*. But a `ViewEffect` on a point where the caster himself stands did not show in game:
  league_thresh R's Box, played in the `end_effects` of Ekko's anchor (which ends on his own spot), was
  invisible (seen by the user, 2026-09-29), though the simulation logs the event
  (`EffectApplyed { target: Pos, caster_id }`, the same as for a far point) and the binding reads back
  normally (`is_follow` false by default). The view layer's effect system carries an `is_rot` flag, but a mod's
  `ViewEffect` never sets it (read from the SDK's game_view, section 6), so the turn is not why; the cause is
  unknown. Play such a picture as a `CasterViewEffect` in the cast (not following), and keep
  `ViewEffect`s for points away from the caster (Ekko's field, Teemo's and Jinx's traps). league_yone's body
  left behind (`e_body` in his anchor's `end_effects`) is the same pattern and has not been seen in game. A `BackToCasterLinearProjectile` started from them flies from that point back to the
  caster, wherever he has walked meanwhile, hits what it passes and runs its own `end_effects` on the caster
  when it reaches him (league_ekko Q; Reimu, Draven and Swain chain it the same way).
- A `ParabolicProjectile`'s `range_effect_name` plays on the landing point the tick it is fired (a
  telegraph for the whole `travel_time`), and the projectile lands where its target stood when it was fired
  *(measured for league_ekko W)*.
- A caster buff lasting 1 tick exists only in the tick it was added: a `SwitchByBuff` later in the same
  tick sees it, the next tick nothing does. A projectile on `EnemyChampion` flying the same path as one on
  `EnemyWithoutTower` (a champion-only twin) sees a 1-tick flag the real one set on the unit both hit that
  tick, whichever was spawned first *(measured for league_ezreal Q: champion-only effects on a skill that
  also clears waves)*.
- A unit killed by an effect still counts as a valid target for the rest of that tick; a `Delayed` effect
  queued on it still runs after it died, but only its pictures and sounds: a `ViewEffect` or `TargetSfx`
  still plays on the body while an `AddCasterBuff` from it is skipped *(league_annie R, 2026-09-28: a
  2-tick caster flag added from such a `Delayed` was there a tick later on every living target and on no
  dead one, 24 games)*; an `AddCasted` on it stops once it is dead. "Kill trigger" and "A summon that
  follows its target" in section 7 are built on these.
- A `RangeProjectile` straight in a `Targeting` cast (or in a `Delayed` of one) never spawns: a zone needs
  a point, as in a projectile's `applied_effects`. A hidden `ParabolicProjectile` with `travel_time: 1`
  lands on the target unit's current position the tick it is fired and its `end_effects` start the zone
  there, which hits the next tick - an area round a unit wherever it walks (league_annie R). In the SDK a dead
  caster fires no projectile, this one included; in the game it does (section 5, "In the game a dead caster's
  `Delayed` effects run").
- An `AddCasted` runs its effects a tick after it is added from an action's effect tree, the same tick when
  added from a `Delayed` effect, then every `period` ticks while fewer than `duration` have passed
  (duration 301, period 60: six runs, 0 to 300 ticks after it was added). Its effects play on the target:
  `ViewEffect`s on the unit, projectiles from the caster. The target's death clears it; the caster's does
  not (its views and a plain `ApAttack` go on). Damage from inside it counts as `attack_type: Dot`, even
  through a zone it started, and a `Fire` one shows a `burn` status icon on the target.
- An `ApplyInProjectile` applies its `applied_effects` once per unit for its whole `tick`: a unit it has
  hit is never hit again by that zone, even after walking out and back in, and a unit that walks in later
  is hit on the tick it touches the edge *(measured for league_thresh R, 2026-09-29)*. Where it starts:
  `follow_caster: false` in a `None` cast never spawned, in a `Targeting` cast it spawns on the target; to
  lay it where the caster stands, start it from the `end_effects` of Ekko's anchor (a `LinearProjectile`
  with `speed` 1, `range` 1, section 7 "Back to where he stood"). `follow_caster: true` in a `Targeting`
  cast spawns on the caster and moves with her for its whole `tick`, each ally it touches hit once - League's
  Melodies (league_sona Q / W / E: 3 logged games, every buff once per ally per cast).
- **Where a line ends: its goal is cut into the map one axis at a time** *(SDK simulation, league_jinx R and
  league_ezreal R, 2026-10-10: 240 logged games each, the ult action's aimed direction against the line it spawned)*.
  A `LinearProjectile` leaves `5000 - y_offset` north of the caster and flies straight to its goal, where it is
  removed; the spawn event's `dir` is that goal minus the start. In a `Direction` cast (a `Targeting` one too) the goal
  is the caster's pivot plus the cast direction x `range`, and then x and y are each cut to 0..959999 (the map is
  960000 square) on their own, so a goal off the map slides back along one axis - or into a corner - and the whole
  line turns toward it. In a `Position` cast the goal is the cast point, or `range` along the way when the point is
  farther: always straight, never past the point. With `range` 1000000 (more than the map) nearly every goal fell
  off: league_jinx R, cast on champions anywhere, turned 7.5 degrees in the median, 23 at the 90th percentile and up
  to 45 (a third of the rockets flew at a corner), and 56% of them struck an enemy champion, 23% the one aimed at;
  league_ezreal R, cast within 120000, turned 8.9 / 27 / 56 degrees and struck 24% (11%). At 300000 a line is cut
  only when the caster stands near an edge (one cast in seven or eight): Jinx's rockets, now cast within 250000,
  struck 67% (43%). Ezreal's waves struck no more champions than before (23%, 13% the aimed one), because **a line
  that comes straight at a champion is dodged**: between the launch and the wave's arrival the aimed champion stepped
  23400 units off the line (median), against 11400 while the waves went astray - 20100 against 3600 for those still
  on the line at the launch (Jinx's faster rocket: 15700 against 4800). So the same casts replayed on a straight line
  (44% for Ezreal) overrate it; measure the new kit's own logs. In the replay a champion counted as struck when its
  centre came within the line's radius + 4000 of the logged projectile, which matched 1334 of the 1336 rockets and
  1267 of the 1280 waves. Jinx's blast had been the rocket's `end_effects`, which run wherever it stops - with
  nobody struck, the map's edge before, the middle of the fight at 300000 - so it now starts from the hit: a
  `Delayed` 1 hidden lob (`travel_time` 1, league_brand's passive) onto the champion struck carries it, a tick after
  the hit, and a miss blows nothing up. **Damage behind a caster flag is not dodged**: gating the end effects with
  a flag the hit sets (or one the launch sets and the hit removes) also blew up only on champions, but the enemy
  champions stopped dodging the rocket (4000-4400 units off the line instead of 15700) and 80% struck instead of
  67% - while it flies, the flag's branch holds no damage.
`ApplyInProjectile` has no `period` and `RangePeriodProjectile` no `follow_caster` (SDK), so an aura
that ticks while it follows the hero is built from `Delayed` pulses of a `RangeEffect` around the
caster (section 7, "Aura that runs while he fights").

Shapes *(`ProjectileShape::is_in` in the SDK's game_core; every radius and half-size also counts the
collision radius of the unit tested, and for RangeEffect the caster's too)*:
- `{"Circle": {"radius": N}}`
- `{"Rect": {"width": W, "height": H}}` - axis-aligned around the centre, never turned
- `{"Line": {"width", "from_x", "from_y", "to_x", "to_y"}}` - a segment with fixed coordinates: they are
  map positions, not offsets from the projectile, so no wall can be drawn round where a hero stands
  (league_thresh R's five walls became one circle). It hits like a capsule: a champion whose centre is within
  `width` + 15000 of the segment, round past both ends (behind the caster too). So `width` is a half-width, and a
  picture of the whole band is 2 x `width` across *(SDK simulation, league_taric E, 2026-10-01: widths 1000, 6000,
  18000 and 30000 hit every champion within 16000, 21000, 33000 and 45000 of the segment and none farther, up to
  28 of 13000-39000 champion positions off)*
- `{"DirDot": {"radius": N, "range": C}}` - a **cone**: within `radius` of the centre and at most
  acos(C / 1000) off the direction from the caster to the centre (`range` 600 = 53 degrees each side). The
  angle is the unit's centre's: the radii widen the distance only, so a big body half in the cone is missed
  *(SDK simulation, league_missfortune R)*.
  Around the caster that direction is zero and the cone is a full circle, so use it with `Forward`.

RangeEffect `apply_type`: `"AroundCaster"` or `{"Forward": {"offset": N}}` - the centre N units from
the caster toward the effect's target (the unit of a `Targeting` action, the point of a `Position`
one; a `Direction` cast falls back to the caster). The Touhou pack's Sanae ult uses Forward + Rect;
league_darius E uses Forward `{offset: 1000}` + DirDot as its cone. `offset` is unsigned (`-20000` is a
parse error), so no area can be put behind the caster.

**Presentation**
`ViewEffect {name}` (play a `view_effects` animation on the target/point),
`CasterViewEffect {name}` (on the caster), `CasterAnimation {name, tick}` (force a sprite tag on
the caster for `tick`; the caster stays in place meanwhile, so move it from the effect tree with
`MoveToTarget` / `MoveTo` / `RushTime`), `RemoveCasterAnimation {name}`, `Sfx {name}` (at caster),
`TargetSfx {name}` (at target). Base `ViewEffect` entries sometimes carry `range/speed/time/radius`.

**Base only - do not use in mods:** `Native` (calls hard-coded logic via `effect_ref`), `AddStatScaledBuff`.

**Data effects since game 0.6** (the official schema's effects.md; the classic SDK's parser does not have them,
so they cannot be simulated, and no hero of this pack uses them yet): `Rush {speed, range, move_speed_ratio,
casting_target, penetrate, applied_effects}` - the caster rushes toward the position input, hitting what matches
`casting_target` on the way (defaults: `casting_target` Ally, `range` 0); `ShrinkingBarrier {name, start_radius,
end_radius, shrink_per_tick, tick, edge_thickness, applied_effects}` - a ring round the target that follows it and
closes, applying at its edge; `TargetProjectileFromProjectile {name, speed, y_offset, applied_target,
applied_effects}` - a homing projectile spawned where the current projectile is (only inside a projectile's
`applied_effects` / `end_effects`).

## 5. buff_state

```json
{"name": "league_garen_q_haste", "duration": {"Time": {"tick": 90}}, "move_speed_mult": 35}
```

`duration`: `{"Time": {"tick": N}}` | `"Permanent"` | `"WithShield"` (lasts while the shield
holds). Some pack buffs omit it - set it explicitly. *(seen in the SDK simulation, league_annie E:
a `WithShield` caster buff added right after her own `Shield {tick: 180}` was gone 180 ticks later
when nobody hit her, and 89 ticks after the cast when enemies broke the shield first.)*

**A `WithShield` picture outlives its own shield** *(player video, league_annie E, 2026-10-07)*: since the buff
stays while any shield holds, league_annie's Molten Shield ring stayed on her 10 s and more in a game where her own
shield lasts 3 s (another shield on her held it; in the simulation an extra 1200-tick shield kept the ring on for good).
A buff that is only the picture of one shield gets a `Delayed {tick: <the shield's tick>}` `RemoveCasterBuff` after
it (league_annie E; then league_blitzcrank, league_camille, league_diana, league_ekko, league_riven and the self casts
of league_janna, league_morgana and league_thresh - with no extra shield the simulation already showed Riven's E ring
219 ticks on a 90-tick shield, Diana's 458 on 300). Not for a `WithShield` flag that asks "does a shield hold" on
purpose (league_malphite's granite, league_rakan's passive: their shields last 36000 ticks, so a timer means nothing).
One given to an ally (`AddBuff` from a `RandomTarget` or a projectile) cannot be taken off: `RemoveCasterBuff` works
on the caster only, also from an `AddCasted` on the ally (its caster is still the giver); those stay `WithShield`.

**`WithShield` to the tick** *(SDK simulation, league_kayle)*: a `WithShield` buff stays while any shield on
the unit holds - also one an ally gave it - and is gone 2 ticks after the hit that breaks the shield, so read it
with a `Delayed {tick: 2}`. A `FixedAttack` on yourself is scaled by `damaged_reduce` / `damaged_amplify` like any
damage, and damage a shield absorbs does not count in the simulation's "tank" statistic. Separate shields are spent in
the order they were added, and a 1-tick `Shield` is gone by the end of the tick it was added in (no `EntityShield` event
shows it) *(SDK simulation, league_kaisa, 2026-10-04: a 39 shield then a 1-tick 100000 one; a hit of 23 left 16, a
hit of 43 cost no health)*. Damage is floored after the reduction (20.5 x 115 = 2357 under 99% hit for 23).
A `Damaged` event carries the whole hit, shield-absorbed or not. In the SDK a dying caster's
zones and pending `Delayed` effects stop (in the game the `Delayed` effects run on: "In the game a dead caster's
`Delayed` effects run" below); the respawned hero is a new entity with none of them. Not a zone started
from a projectile's `end_effects` (or a `Delayed` there): it runs its whole life (league_caitlyn W's traps, thrown as
projectiles, 2026-10-01; see "A dead caster").

**A dead caster** *(SDK simulation, league_jinx E, 2026-10-01)*: until he respawns (as a new entity) his buffs
keep the state they had when he died - `SwitchByBuff` still reads them, nothing can be added to or taken from
them (also straight in a projectile's effects, not only from a `Delayed`), and timed ones do not run out.
Projectiles started from another projectile's `end_effects` still spawn and hit; a `Delayed` queued after the
death still runs its effects, but a projectile it starts does not spawn (a dead caster fires no projectile).
league_jinx E's links went on after her death and, with the lock never added, bit the champion they had rooted
at every link (8 and 18 times in two of 24 games; players: "夹子反复触发"); each check then started from a
`Delayed {tick: 1}` and a dead Jinx's trap bit no one in the simulation (0 in 51 games) - but players saw it again
on that version, so the game spawns what the SDK does not (league_riven R below): the trap is now `Delayed` effects
of the cast itself, which the SDK stops when she dies and the game does not - there each link's heartbeat, a flag
the link before it added, ends the trap one link after her death (section 7, "A trap that waits and snaps once").
A flag the trap puts on her while she
lives and reads later cannot do it: any flag on when she dies stays on, and gates that are off when the AI decides
cost casts (section 3: the AI scores the branch the caster's buffs pick). A search can: `RandomTarget {range: 1,
casting_target: AllyOnlySelf}` finds no dead caster, so a zone's applied effects can ask "does she live" (a 1-tick flag
from the search, read and taken off in the same run) and keep their effects in plain sight of the AI - league_caitlyn W: 0
bites after 29 deaths in 16 games (285 unguarded), the AI's throws unchanged, where the `Delayed`-projectile route cost a
third of them. Take the flag off right after reading it (`RemoveCasterBuff`, same list): a 1-tick flag lasts to the end
of its tick, and a caster killed later in that tick keeps it on for good, so every later check passes (league_caitlyn
W's `w_live` and league_jhin E's `e_live` were left on until 2026-10-07: a caster dying in the tick one trap went
off would have had the other traps go off every tick).

**In the game a dead caster's `Delayed` effects run, and fire projectiles** *(player video, league_riven R,
2026-10-07)*: Riven died in a fight and 14 s later her Wind Slash, launched three times about a second apart from a
cast's `Delayed {tick: 300..1470}` checks of `league_riven_r_slash_ready`, hit an enemy champion for 401 each while
her respawn timer ran (「瑞雯死后放三次大招连放三次」). The SDK stops those `Delayed` effects at death and spawns no
projectile from a dead caster, so no simulation showed it; and since her buffs froze when she died, the
`RemoveCasterBuff` after each slash took nothing off, so every later check fired again. Every check now runs inside
`RandomTarget {range: 1, casting_target: AllyOnlySelf}` (the search above that finds no dead caster): with her alive
the slash rate and its hits are unchanged in the simulation (21 slashes in 62 R casts, 1.7 hits each, against 28 in
70 and 1.7 before - different games past the first R). Any `Delayed` chain that deals damage, starts a projectile or
reads a flag the cast set should be guarded the same way.

**Which chains need the guard** *(audit of the 60 released heroes, 2026-10-07)*: what matters is what gates the
harmful branch of a `Delayed` that runs after the caster may have died.
- Safe as it is: a branch behind a caster flag the same run adds just before reading it - a search adds a 1-tick
  flag, `SwitchByBuff` reads it - since a dead caster adds nothing (league_blitzcrank R's `r_go`, league_akali R2's
  `r2_t` from a hidden check, league_nocturne E's fear, league_morgana R's tethers). A flag added a tick or more before
  the read leaves a window: a caster killed in it keeps the flag on, and every later check passes (league_taric R's
  `n2`, added a tick before each fire check - a dead Taric would have made the allies round his body invulnerable
  every 30 ticks; guarded). A heartbeat, each link reading the flag the link before it added, ends a chain one link
  after the death (league_jinx E: one more trap check, one bite at most).
- Unsafe: a branch behind a flag the cast set and only a timer or a later effect takes off - a channel, a window, a
  count - or behind none at all: frozen on, it fires to the end. Guarded on 2026-10-07: league_lucian R (shots on
  `r_ch`), league_missfortune R (waves on `bullet_time`), league_fiddlesticks R (storm, 5 s) and W (drain),
  league_janna R (heals), league_diana W (the orb count it takes off froze, so every check while an enemy stood near
  her body fired another orb), league_amumu's Despair pulses, league_leona W's Eclipse burst, league_ekko R's rewind
  (a `Delayed` in the anchor's `end_effects`: the SDK runs it after his death too), league_garen E (no flag: six more
  spins), league_rakan R's later rushes, league_taric R; league_yone E's echoes read a flag his return adds (section 7).
- Left: one effect League's own spell lets finish (league_kayle R's blades, league_taric R's invulnerability 2.5 s
  after it fired, league_zilean R on an ally, league_jhin's lotus blooms, league_fizz R's shark, league_annie's
  Tibbers), effects on the dead caster only (league_blitzcrank's barrier, league_evelynn's camouflage chain and its
  one "shade" sound, a `Teleport` of the body: league_yone E, league_twistedfate R), chains of about 1.7 s or less
  (league_aatrox W, league_jax E, league_leblanc E, league_lissandra, league_nocturne E's ticks), league_fiora R (her
  `r_alive` is added a tick before each read, and its heal needs every vital struck), and league_kayn R (he takes no
  damage inside his target).

The guard goes only on a `Delayed` that does something a player sees - damage, healing, a projectile, a move, a
picture or sound; one that only adds or takes caster flags is harmless dead and is left alone (wrapped, league_lucian
R's end-of-channel flag swap changed: inside the search its `SwitchByBuff` caught `r_ch` on the tick it ran out, which
the bare one had missed). It has two shapes. When nothing in the `Delayed` uses the action's own target, point or
direction (caster flags, caster pictures and sounds, `RandomTarget`, `RangeEffect` `AroundCaster`), its effects go
inside the `RandomTarget {range: 1, casting_target: AllyOnlySelf}` (league_riven R; 1 effect node). Otherwise - a zone
at the cast point, a `Forward` area, an effect on the unit a projectile hit - inside the search they would land on the
caster (league_missfortune R's waves flew with direction (0, 0)), so the `Delayed` runs `RandomTarget AllyOnlySelf ->
AddCasterBuff <hero>_lives {tick: 1}`, then `SwitchByBuff <hero>_lives` with the effects as `effect_buff` and the same
effects inside a `RandomTarget AllyOnlySelf` as `effect_none`, then `RemoveCasterBuff <hero>_lives` (league_missfortune
R, league_ekko R). The `effect_none` copy is for the AI: units read other units' pending effects through the branch
their buffs pick at that moment, when the 1-tick flag is always off - with an empty `effect_none` enemies stopped
seeing league_missfortune R's waves and league_yone E's echoes, and the games parted (29 of 30 seeds for Yone); a
`RandomTarget` they read through. The copy doubles the effects, so mind skill and skill2, which the game copies every
tick (docs/perf.md) - why league_yone E's 108 echoes use the return's flag instead.

To check a guard: the search draws from the game's random numbers, so a guarded hero's games part from the unguarded
ones after the first guard. Compare instead against a control kit with the same search and flag but no gate (the
effects run anyway): the hero's event logs must match tick for tick while he lives (`EntityInfo` snapshots aside - a
flag on and off within a tick changes when they are sent). 2026-10-07, 30 seeds x 600 s each (`evlog.exe 600 <seed>`):
league_lucian, league_missfortune, league_fiddlesticks, league_janna, league_diana, league_amumu, league_leona,
league_taric, league_ekko, league_rakan, league_caitlyn and league_jhin matched in all 30 - 1648 R bullets, 1402
waves, 1829 orbs, 291 Eclipse bursts, 45 Cosmic Radiances, 96 rewinds among them; league_garen in 11, the other 19
parting only after his death: the control's E spun on round a dead Garen, so the SDK does not stop every pending
`Delayed` either. Before the AI-visible `effect_none` and before league_lucian R's flag swap was left unguarded, the
same check caught both.

**Death clears a mod's buffs** *(seen in the SDK simulation, a probe hero on league_teemo)*: a
`Permanent` caster buff added by his first attack was missing from his buff list after he died and
respawned, until his next action added it again; so were league_teemo R's slot buffs. Item buffs and
the serpent's permanent buff stayed. So a `Permanent` "init" flag that every action checks first
fires once after each spawn: league_annie starts the game and every life with Pyromania's stun ready,
as League's Annie does (section 7).

`hp_regen` is health per second (the base UI: "HP Regen per Second"). `undying: true` keeps the
unit alive while the buff lasts (Touhou Mokou's ult, LoL Reborn Sion's R).

Fields seen (count across packs): `range` (attack range bonus, 278), `move_speed_mult` (235),
`attack_speed_mult` (160), `magic_power_mult` (122), `attack_mult` (115), `hp_mult` (115),
`base_attack_enemy_max_hp_damage` (on-hit % max HP, 111), `skill_cooldown_mult` (110),
`damaged_reduce` (% less damage taken, 74), `defence_mult` (72), `magic_resistance_mult` (70),
`vamp` (lifesteal %, 66), `toughness` (tenacity, 58), `damage_reflect` (56), `cc_immune` (bool),
`radius_mult`, flat `attack` `defence` `magic_resistance` `hp` `magic_power` `crit_chance`
`hp_regen`, `ignore_wall`, `undying`, `damaged_amplify`, `ult_cooldown_mult`, `defence_penetration`,
`heal_reduce`; the engine also reads `dot_amplify`, `self_max_hp_damage`,
`skill_enemy_max_hp_damage`, `base_attack_damaged_reduce`, `skill_damaged_reduce` and
`magic_resistance_penetration`.

`skill_cooldown_mult` does not make cooldowns run faster: every tick it caps each remaining cooldown
at cooltime x 100 / (100 + mult), skills at 3 ticks or more, the ult with `ult_cooldown_mult` added
*(measured in the SDK simulation for league_ezreal, 2026-09-29; this page used to read
`Entity::cooldown_reduce` as "a cooldown advances 100 + mult per 100 each tick", which the probes
disproved)*. So it works as a refund at the moment it appears: +40 cuts a skill with most of its
cooldown left to 71% of the cooltime and then does nothing more while it lasts, +100 to half; a buff
that lasts 1 tick changes nothing, 2 ticks are enough. Stacked instances add up, and each new one
lowers the cap again (a permanent +100 added on every attack had league_masteryi cast Q 162 times in
10 minutes). While it is active it also speeds the hero's skill actions (their speed multiplier, so
`start_timing` comes sooner), but not the `Delayed` ticks inside them. LoL Reborn's Lucian and Ezreal
refund cooldown with short bursts of it; league_masteryi's Highlander gives +40 for its 7 s in place
of League's takedown refunds. No slow immunity exists: slows are buffs, and `cc_immune` and
`toughness` only touch CC.

**How buffs stack** *(read from the SDK's game_core, not yet seen in game)*. `is_hidden`,
`can_stack` and `max_stack`, common in packs, are not buff fields at all: the engine's parser skips
unknown keys and the game binary does not contain those names. Every `AddBuff` / `AddCasterBuff`
pushes one more instance, even with a name already present, and the stats of all instances are
added up; `RemoveCasterBuff` removes every instance with that name and `SwitchByBuff` asks whether
any exists. So a stat buff added again while it runs doubles (guard it with `SwitchByBuff`, as
league_darius does for Noxian Might), a counter buff needs no fields, and a buff without a
`view_buffs` entry is invisible anyway. Summed `*_mult` values stop at -99% (100 + sum is clamped to
at least 1), so two slows cannot push a unit backwards.

## 6. View bindings

Effects only simulate; nothing is drawn unless a view entry with the **same name** exists in
the same champion file.

```json
"view_projectiles": [{"type": "Animated", "name": "league_garen_wave", "anim": "asset/league/fx/league_garen_wave", "tag": "fly", "repeat": true, "z": 0}],
"view_effects":     [{"type": "Animation", "name": "league_garen_q_hit", "anim": "asset/league/effects/league_garen_hits", "tag": "q", "z": -1, "is_follow": true}],
"view_buffs":       [{"type": "Animated", "name": "league_garen_judgment", "anim": "asset/league/effects/league_garen_spin", "tag": "loop", "z": 1}]
```

- `view_projectiles` <- the `name` of any projectile/zone effect. Also `{"type": "Sprite", "name", "sprite"}` for a static image.
- `view_effects` <- `ViewEffect` / `CasterViewEffect` names (and `range_effect_name`).
- `view_buffs` <- `buff_state.name`. `{"type": "ThreePhase", "pre_tag", "loop_tag", "remove_tag"}` gives an intro/loop/outro buff.
  All three tags are required (without `remove_tag` the SDK's parser refuses the kit: `sdk_probe` "missing field
  `remove_tag`"). league_janna's storm shield plays Eye of the Storm's forming as `pre_tag`, the storm while the
  shield holds as `loop_tag` and the forming played backwards as `remove_tag`: a separate `ViewEffect` for the
  intro would play on top of the buff's loop.
- `z` < 0 draws under units (ground decals, zones); `is_follow` makes an effect follow its unit.
- How the client builds a mod's views *(read from the SDK's game_view 0.5.1, 2026-10-05:
  `GameViewSystem::register_data_champion_views` and the systems' `render` / `generate`)*: an `Animated`
  `view_projectiles` entry becomes an `AnimatedProjectileSystem` with its turn on and no spin (`render` draws the
  sprite with `RenderCommand::rot` of the projectile's angle), and `Sprite` and `ThreePhase` turn too - so every
  projectile's or zone's picture follows its direction, never a flip. A `view_effects` `Animation` becomes an
  `AnimationEffectViewSystem` whose `is_rot` and `render_at_caster` are always off and whose `is_follow` is the data's;
  `generate` makes an `AnimationOnce` on a point (never turned: only `is_rot` calls `atan2`), an
  `AnimationOnceFollow` on a unit with `is_follow`. 1 px is 1000 units (`generate` scales positions by 0.001).
- The whole schema (serde names in the SDK's `game_core` metadata): `view_effects` are `Animation` or
  `LoopAnimation`, each `{name, anim, tag, z, is_follow}`; `view_projectiles` are `Animated
  {repeat}`, `Sprite` or `ThreePhase {pre_tag, loop_tag, remove_tag}`. There is no rotation or flip
  field: how a view is placed depends on what plays it.
- A projectile's view is turned to its direction (a `LineRangeProjectile` rectangle: drawn pointing
  right, see "Cone / fan"), so cast upward it lies across the screen and cast left it is upside down.
  That includes a ground zone's view: a `RangePeriodProjectile` on a `Position` cast gets a direction of
  (1, 0) or (-1, 0) *(SDK simulation log)*, and league_missfortune E's falling rain, drawn as the zone's view,
  rained upward whenever she cast it leftward (seen in-game in the mid lane). A picture that must stay
  upright goes in a `ViewEffect` next to the zone in the cast's `Combine` instead (no view for the zone):
  on a `Position` cast it plays on the cast point in the same tick, unturned (an `Animation` plays its tag
  once, so its frames cover the zone's lifetime). The same went for league_leona R's sunlight (a `RangeProjectile`;
  the user: 「曙光女神大招在红色方放的是颠倒的」, 2026-10-05), league_varus E's ground, league_soraka Q's star (drawn
  falling from the top left, cast leftward it rose from below; the zone sits in both branches of her Equinox switch,
  a `ViewEffect` next to each) and league_lux E's ring with the orb above it - a zone started in the lobbed orb's
  `end_effects`, so its `ViewEffect` plays on the landing point (section 4) - all `ViewEffect`s now, their zones
  without a view. A zone's picture is turned about its pivot (the frame's centre), so a ring drawn on the ground
  line, 11 px under the pivot as the feet are, also floats 22 px higher when turned *(inferred from the frames'
  anchors)*: only a picture that looks the same turned half round about its pivot is safe as a zone's view.
  `lint_mod.py` warns on every zone (`RangeProjectile`, `RangePeriodProjectile`, `ApplyInProjectile`) that has a
  `view_projectiles` picture, wherever it is cast, with the share of the picture that lands elsewhere turned half
  round. On 2026-10-05 it flagged 8 in 5 heroes; the user had the doubtful ones fixed the same way (「众星之子 E /
  丽桑卓 R / 娑娜光环按同样的方法修」): league_soraka E's field (a ring on the ground line: a `ViewEffect` in its
  `Delayed`), league_lissandra R's field (upright icicles: a `ViewEffect` in each of the six lobs' `end_effects`) and
  league_sona's three auras (upright notes on a ring round her: each a `CasterViewEffect` with `is_follow: true` at
  the action's own tick, next to its follow-zone `ApplyInProjectile`, its tag held for the aura's 180 ticks - the
  loop repeated, `strips.write_sheet(share=True)` packing the repeats once). It still flags league_camille R's two
  (stored turned on purpose: her zones always get (-1, 0), section 7) and league_fiddlesticks E's reap (a crescent
  drawn facing the cast, symmetric top to bottom: meant to turn with it).
  **The client never mirrors an effect picture** *(game_view and TeamfightManager2.exe disassembled, 2026-10-06)*.
  A `ViewEffect` or `CasterViewEffect` is drawn exactly as stored whichever way the hero faces, `is_follow` or not:
  `register_data_champion_views` builds each `view_effects` entry's `AnimationEffectViewSystem` with its flip byte
  set to 0, `generate` copies that byte into the `AnimationOnce` / `AnimationOnceFollow` it makes (both the SDK's
  0.5.1 and the shipped exe's), the match event handler appends the view unchanged (for a following one it only
  drops an older play of the same picture on the same unit), and `EffectView::render` passes that byte to
  `RenderCommand::flip_x`. `get_action_flip_x` (caster left or right of the action's target) only sets the hero's
  facing for an action. `view_buffs` pictures are not mirrored either. The hero's own frames are: so a picture drawn
  pointing right points right on the red side too. Until 2026-10-05 this file said a non-following caster picture
  took the caster's facing (inferred, never seen): the "red side" fixes of 2026-10-03 and 2026-10-05 that set
  `is_follow: false` or moved a picture to the action's start (league_vi E and R, league_aatrox Q, passive and W,
  league_caitlyn, league_jhin, league_kaisa W and R, league_leblanc, league_kennen Q, league_ryze Q,
  league_diana, league_tristana Q) changed nothing in game - league_jhin's muzzle flashes still pointed right on the
  red side (「烬在红色方 玩家反应 技能特效 伤口还是反的」, 2026-10-06). What looked like mirroring before was
  where the picture stood: league_tristana's flashes 22 px in front of her pivot were behind her after she turned,
  league_fiora's parry crescent (a buff picture 17 px in front) behind her when she faced left.
  So (the whole pack went through this on 2026-10-06, `tools/fix/red_side_caster_fx.py`, which lists what each hero
  got):
  - **A picture with a front and a back that rides on the hero is drawn into his own frames.**
    `assets/source/native/<hero>_bake.json` (`{"fx": "<effect sheet>", "items": [...]}`, one item a line, applied in
    order) is read by `tools/art/import_native.py`: `{"tag", "into", "at_ms", "under", "fx"}` draws the effect tag
    into the action tag from `at_ms` on, centred on the pivot as the `CasterViewEffect` was (both are drawn centred
    on the unit), under the body when the view's `z` was below 0, cutting the frames where an effect frame starts or
    ends and padding them to one canvas (frames of any size are drawn centred). `tools/fix/bake_caster_fx.py --hero
    <hero>` writes the items and changes the kit: it times every play of a flagged picture - the action's effect
    fires at `start_timing` + 1, plus the `Delayed` ticks over it, a lob's `travel_time`, a penetrating
    `LinearProjectile`'s flight to its range - and finds the animation on him then: the action's own, or the last
    `CasterAnimation` started in the same effect list (everything in a list happens in the same tick, so one started
    after the picture in the list counts: league_garen's E pulses play the picture, then start the spin again), in a
    `Combine` in it, or in a Switch in it whose branches start different ones (league_aatrox Q: `skill_r` in his R,
    `skill` out of it - the play follows its own branch of the same Switch fields, or is split the same way).
    - A play under no condition its animation was not started under, in a tag started in one place only: the
      picture is drawn into that tag and the `CasterViewEffect` goes. Nothing the game runs changes.
    - Any other play (only some casts show it: a Switch branch, a lob's `end_effects`): the `CasterViewEffect`
      becomes a `CasterAnimation` of a copy of the animation on him then, from that moment on, with the picture
      drawn in (`{"from", "slice_ms", "length_ms"}`: the copy is made first, looping a tag held longer than it
      lasts). **A `CasterAnimation` keeps the unit from walking**, so the copy ends where the animation it replaces
      would have: as long as a `CasterAnimation` it cuts short, within the action for the action's own (a first try
      held league_aatrox W 2 ticks past his action and the simulated games went another way). A
      `RemoveCasterAnimation` of the source tag gets one of each copy next to it. Starting an animation still nudges
      the simulated AI by a tick now and then, which is why the first way is taken whenever it fits.
    - A picture that runs more than 150 ms past the animation it would be drawn into played on while he walked: it
      is left, unless it is a dash trail or flash whose tail may be cut there (`--cut`: league_kaisa R, league_vi Q
      and R, league_aatrox Q3, league_tristana Q).
    Checked against the SDK simulation (old kit and new, the same seeds, `EntityEvent Action / Animation` and
    `EffectApplyed`): every play landed in the copy or the tag it was drawn into at its time. Attack speed shortens
    the effect's `start_timing` to `floor(start_timing x 100 / speed) + 1` ticks but not the `Delayed`, so a baked
    picture, which plays with the animation, now keeps to the shot frame where the old one drifted.
  - **A caster picture the hero's frames cannot carry is made left-right symmetric**: an aura, shield or burst
    replayed while he walks (league_tristana's Rapid Fire wisp, league_masteryi's Highlander, league_kaisa's E) or
    played when a projectile hits (league_jinx's Get Excited, league_varus's rage). `tools/fix/mirror_union_fx.py`
    draws each frame over its mirror image into `league/effects/league_<hero>_sym` (a tag per picture, its source in
    `assets/source/native/<hero>_sym.json`; rerun after the source sheet changes) and points the view there.
  - A picture on a target or a point (a hit, a burst) is mostly symmetric already; one that shows where the blow came
    from - a streak or chevron pointing on along the shot (league_ezreal R, league_riven's Wind Slash, league_yasuo Q
    and E, league_vayne's bolts) - is made symmetric the same way. A slash or crescent across the target reads the
    same either way.
  - A picture that must point at the target rides a projectile, which is turned with its direction (below).
  - **A figure of the hero left on the ground while he moves on is drawn from the front.** It is no one action,
    nothing reads his facing, and a projectile's picture turned half round stands upside down - but a figure facing
    the viewer faces no way. league_yone's E body was one already (it only stood 4 squares right of its spot: its
    pivot moved in `yone_cells.json`); league_ekko's R hologram was made from his side-on idle and is made from Codex's front view now
    (`assets/source/red_side/ekko_front.png`, `PROMPTS.md`, `tools/art/pack_red_side_figures.py`, `import_ekko.py`). league_shaco's R clone needs none:
    it always stands left of the champion it strikes, facing him, whichever side Shaco cast from.
  `lint_mod.py` warns on every caster picture whose mirror leaves more than half its pixels on empty ones (137 in 46
  heroes before the pass, none after); `tools/art/bake_gifs.py --hero <hero>` draws the blue side and
  the red side before and after (`docs/preview/red_side/<hero>_bake.gif`). An `Animation` plays its tag once, so a
  view that must stand for seconds lists its loop frames again (a 4 s loop of 100 ms frames is 40 frames). A
  `CasterViewEffect` stays where it was played unless `is_follow`; a following one cannot be stopped: refreshed before
  it ends, the next one plays over it.
  A picture that must face the target goes on a `TargetProjectile` cast at it
  (league_lucian Q's way: it points from the caster's pivot at the target and `y_offset` lifts only its picture):
  league_fiora's parry crescent rides one with `speed` 100 and `y_offset` -4000 (9 px up), drawn 17 px ahead along its flight and
  mirrored top to bottom, each 6-tick frame stepped back by the distance crept, an empty last frame after the
  parry's 45 ticks while the projectile crawls on (4-9 s in a logged game; it goes at once if the target dies).
  A picture that must outlive a target killed by the hit rides a view-only `LineRangeProjectile` instead (in a
  `Targeting` action it points at the target and lasts its `delay`; league_briar E's scream, league_vi E's shock wave:
  as a caster picture it stood the wrong way on the red side, "E技能的特效没有跟随人物 反方向的").
  A thing with a top and a bottom that flies every way (league_thresh's lantern) is laid along its flight
  and mirrored top to bottom, so every turn of it looks the same (art-spec). Or it flies without a picture and is
  stamped where it is: league_yasuo Q3's whirlwind, an upright funnel on its `LinearProjectile` (upside down flying
  left, on its side flying up or down; the user kept the funnel, 2026-10-05: 「亚索的旋风特效还是用这个 右边的话你想办法处理
  一下」). The whirlwind lost its `view_projectiles` entry; next to it in the same `Delayed`, 16 hidden
  `LinearProjectile`s (`league_yasuo_q3_step`: its speed, no radius, no effects) stop where it is on every other tick
  of its flight, and each one's `end_effects` play one frame of the funnel's loop as a `ViewEffect` on its stop point,
  never turned (`league_yasuo_q3_tornado_<i>`: tag `tornado_<i>`, the frame showing at that tick, held 34 ms - a
  little over the 2 ticks, so one stamp is not gone before the next; `tools/fix/fix_yasuo_q3_stamps.py`,
  `tools/art/import_yasuo.py`). The funnel steps 5 px 30 times a second along the true path, whichever way it flies.
  Where a `LinearProjectile` is *(SDK simulation, 2026-10-05: hidden ones of every range from 1 to 80000 at speed
  2500, each playing a `ViewEffect` where it stopped, and `ProjectileMove`)*: it moves one step in the tick it spawns
  and each tick after; it stops on the first tick its travel reaches its range and plays its `end_effects` on its
  range exactly, so a projectile that stops on tick t of its flight has range speed x (t + 1) from the third tick on
  (2500 stopped on tick 1, 5000 on 2, 7500 and 10000 on 3, 12500 on 4, 15000 on 5, the whirlwind's 80000 on 31).
  Some casts start the flight a tick later or sooner, but projectiles fired together keep together, so the stamps stay
  on the whirlwind. `ProjectileSpawnData` gives the start 5000 above the caster's ground point and `dir` from there to
  where it will end (the client's picture is turned to that).
- A projectile's picture has one length, but its frames can follow the flight: an `Animated` view with
  `repeat: false` plays its tag once from the moment the projectile appears. league_thresh Q's chain is
  drawn frame by frame (a frame every 2 ticks, 11 px longer each, behind a hook flying 5500 a tick), so its
  end stays on the spot he threw from instead of reaching out behind him; the hook coming back shortens it
  (drawn for the distance most hooks catch at, 55 px in the simulation). The last frame is held longer than
  any flight, so the tag never runs out (whether a finished view holds its last frame or vanishes is
  untested).
- Every `anim` + `tag` must exist. Name typos fail silently - LoL Reborn's Nocturne binds
  `nocturne_attack_hits` while the effect is `nocturne_attack_hit`, so that hit never shows.

## 7. Patterns that work

**Every Nth basic attack is empowered (passive).** Chain `SwitchByBuff` on hidden stack buffs
(template `templates/mymod/champion/hero.data_champion` does 3 hits; Nocturne does 6):
```json
{"type": "SwitchByBuff", "buff_name": "x_stack_2",
 "effect_buff": {"type": "Combine", "effects": [ <empowered hit>, {"type": "RemoveCasterBuff", "name": "x_stack_2"} ]},
 "effect_none": {"type": "SwitchByBuff", "buff_name": "x_stack_1",
   "effect_buff": {"type": "Combine", "effects": [ <normal hit>, {"type": "RemoveCasterBuff", "name": "x_stack_1"},
                   {"type": "AddCasterBuff", "buff_state": {"name": "x_stack_2", "duration": "Permanent", "is_hidden": true}} ]},
   "effect_none": {"type": "Combine", "effects": [ <normal hit>,
                   {"type": "AddCasterBuff", "buff_state": {"name": "x_stack_1", "duration": "Permanent", "is_hidden": true}} ]}}}
```

league_masteryi's Double Strike counts to four with `ds_1`..`ds_3` of 240 ticks each (League's
stacks fall off 4 s after the last attack), so the chain restarts out of combat. The fourth attack
lands its first hit at `start_timing` like any other (attack speed still shortens it), then plays
`CasterAnimation attack2` (League's second slash) with the second hit in a `Delayed` 8 ticks later;
his skill2 adds `ds_3` directly, so the attack after it strikes twice.

**Skill empowers the next attack.** The skill adds `x_ready` (Time buff); `attack` starts with
`SwitchByBuff x_ready` -> empowered effect + `RemoveCasterBuff x_ready`.

**Recast / charges.** `cooltime_use_count: N` on the action (base Nightmare fires 3 shards) makes N
charges that come back one at a time *(measured in the SDK simulation for league_teemo R, from the
`EntityUltCooldown` events)*: every use adds `cooltime / N` (shortened by cooldown reduction) to a
cooldown pool that drains a tick at a time, and the action can be used while the pool is at most
`cooltime - cooltime / N`. So `cooltime` 3600 with 3 uses is League's three charges refilled every
20 s, not three uses a minute. The AI spends them as targets come (league_teemo threw three mushrooms
within 3-6 s, at different spots), not all on one tick.
For different 1st/2nd casts, add a short `x_recast` buff on first cast and `SwitchByBuff` on it.

**Dash then hit.** `MoveTo` (direction) or `MoveToTarget` (unit) with `end_effects:
[ViewEffect, RangeEffect{Attack, Stun}]`. Add `CasterAnimation` with a dash tag for the travel.

**Telegraphed AoE.** `RangeProjectile {delay, apply}` / `LineRangeProjectile {width, length,
delay, apply}` / `ParabolicProjectile {travel_time}`; or `ViewEffect warning` + `Delayed {tick}
RangeEffect`. The two range projectiles hit once, `apply - 1` ticks after they appear, and last
`delay - 1` ticks (section 4): set `apply` to the frame of the picture that lands, and `delay` to at
least `apply`, or to the picture's length (a view appears to end with its projectile, *inferred*).
league_leona R: a `Position` cast on an
enemy champion, two circles (damage and slow; the stun in a smaller centre) with delay 60 and apply 38,
so the flare hits 0.62 s after it appears (League's 0.625 s) and its 1 s picture plays out.

**Cone / fan (Ashe W).** No projectile takes an angle, but `LineRangeProjectile` in a
`casting_type: Direction` action is a line from the caster toward the target, and its view
sprite is centred on the line and turned to the cast direction: drawn pointing right from
x = -length/2 to +length/2 (measured on LoL Reborn's Swain Q fan, Lux R and Jhin W sprites). So a
fan sprite with its apex at x = -length/2 starts at the caster. The hit area is not a rectangle
`width` wide *(SDK simulation, league_ashe W, 2026-10-01: a probe hit picture, every enemy unit's place
along and across the line on the hit tick, 3 games per width)*: a unit is hit when its centre is within
about `width` + 15000 of the segment from the caster to `length` ahead - a capsule, so `width` works as a
half-width, and the round ends reach that far past the tip and behind the caster (champions hit up to
59.6k from the segment and missed from 61.4k at width 45000, 73.1k / 74.7k at 60000, 102.7k / 107.1k at
90000; minions and monsters the same). Draw the fan about as wide as that band. league_ashe W: width
45000, length 80000, delay 17, apply 14 (the hit at tick 13, when the arrows have flown out; until 0.10.0
delay 14, apply 3 hit at tick 2, as the fan appeared), 13 arrows 7 deg apart over +-42 deg (+-50 px at
the tips; until 2026-10-01 9 arrows, League's count, over +-28 deg: +-35 px, found too narrow, against
the +-60 px band it hits), 7 frames x 40 ms, view `repeat: false`.

**Zone / aura.** `RangePeriodProjectile {tick, period}` for a placed field;
`ApplyInProjectile {follow_caster: true, tick}` for an aura around the hero.

**Delayed detonation (Gragas Q, Lux E).** A `RangePeriodProjectile` whose `period` is longer than
its `tick` hits once, at `first_delay`; its view (`repeat: false`) carries the fuse and the
explosion, timed so the blast frame lands on `first_delay` (LoL Reborn Gragas: a
`ParabolicProjectile` whose `end_effects` hold the zone with tick 106, first_delay 75, a 1.75 s
view). A second zone with a short `period` and a short slow buff is the slow field
(league_lux E: field tick 60 / period 10 / 15-tick slow, blast tick 84 / first_delay 60). Pack
authors match a zone's view length to its lifetime (Gragas 1767/1750 ms, Utsuho 1500/1500, Aatrox
633/640), so a view appears to end with its projectile *(inferred)* - draw the blast inside it.

**Long laser with a telegraph (Marisa, Lux R).** Split the look from the damage: one
`LineRangeProjectile` with empty `applied_effects` and a long `delay` carries the view (thin
line, charge, beam, fade), a second one with the same shape whose `apply` is the frame the beam fires
deals the damage (Touhou Marisa: visual delay 120; league_lux R: visual delay 55, damage delay 29 and
apply 29 - the hit at tick 28 with the beam and its sound; until 0.10.0 apply 3 hit at tick 2, 0.43 s
before the beam showed - 240000 x 16000).
The view is drawn at the unit's pivot height and turned to the cast direction, so keep the beam
centred vertically in its canvas (an offset would flip when she fires to the left) *(inferred)*. To draw
it from a raised weapon instead, see "A beam from a raised weapon" below.

**A beam from a raised weapon (league_lucian Q).** A picture turned with a direction cannot carry a
height of its own (an offset in its canvas turns upside down with a leftward cast), and every direction the
engine gives is taken between points at pivot height, so a raised start tilts it *(all SDK simulation logs,
2026-09-29)*:
- a `LinearProjectile` starts `5000 - y_offset` units north (-y) of the caster (default 0: 5000; 12000: 7000
  south; -7000: 12000 north) and heads for the caster's spot plus the cast direction times its `range` (a
  `Direction` cast) or for the target's spot (`Targeting`), and is removed when it gets there. Raised 12000
  with the line's `range` it leaned 7 degrees onto the line's end (the user: "放出来的技能怎么是歪的");
  with `range` 15 it pointed nearly straight down; with `range` 1000000 its goal was cut to the map
  (x at 960000), which turned it further (section 4, "Where a line ends");
- `y_offset` on a `LineRangeProjectile` is ignored (the line does not move);
- a `LineRangeProjectile` started in a projectile's `end_effects` is drawn at that point but points from the
  caster to it (from a point above him: straight north);
- a `TargetProjectile` (and a `TargetSplashProjectile`) is lifted `5000 - y_offset` above the caster's pivot
  and flies from there at its target's pivot *(its move events, league_lucian Q, 2026-10-01: 96 of 103 within 1
  degree of that line; this file used to say it stays on the pivot)*, so its picture runs nearly level with a
  line cast at the same target. But it goes the tick its target dies. It is spawned with no direction (0, 0)
  and its first move, in the same tick, is the whole lift plus one step: the game turns a view by the change of
  position, so for that tick the picture points nearly straight up - league_lucian's full 80 px beam flashed
  upward for a tick on every Q (the user: "一道射在固定角度，再向目标射一道"). Start such a view with an empty
  frame of one tick (`import_lucian.py` `RAY_SKIP`).
Lucian's Q is therefore a `Targeting` cast (on `EnemyWithoutTower`; a `LineRangeProjectile` in a
`Targeting` cast points at the target, as league_yone's W and R): the damage stays on the line, with no
picture, and `q_ray`, a `TargetProjectile` at the target with `speed` 1000 and `y_offset` -8000 (between
the two muzzles of the firing frame; -7000 on the first model), carries the beam: an `Animated` view (`repeat: false`) of one frame a tick,
each drawn 1 px further back than the last (league_thresh Q's chain), so the beam stands still from the
muzzle, then an empty frame while it creeps on to the target. Minions the Q kills took the picture with
them after two ticks, so the line hits 6 ticks after it appears (`apply` 7), at the end of the beam's full
glow: then only the fading goes with a killed target.

**Burn / poison.** `AddCasted {casted_type: Fire, duration, period, effects: [ApAttack]}`.

**Untargetable window.** Only `Banish` makes a unit untargetable (in a `RangeEffect` on `AllyOnlySelf`;
a `WithSelf` would banish the action's target too), and a banished unit sees nothing for its team (section 4): fine
for a caster that leaves the fight, not for one in the middle of it. `Invisible` only hides the unit
from afar. For a caster who stays among enemies: `CasterInvisible` plus a caster buff with
`damaged_reduce: 100` and `cc_immune` - enemies next to it still pick it and swing, but every hit
deals 1 damage (the engine's minimum; a fountain's fixed damage still lands).

**Invulnerable blink strikes (league_masteryi Q, Alpha Strike).** `Targeting` on `EnemyWithoutTower`:
`CasterInvisible {tick: 48}` and a 48-tick caster buff (`damaged_reduce: 100`, `cc_immune: true`)
first, `Teleport` onto the target and strike it, then three `Delayed` bounces 12 ticks apart, each a
`RandomTarget {range: 35000, casting_target: EnemyWithoutTower}` whose effects are `Teleport` and the
strike; a last `Delayed` `Teleport` puts him back on the first target. In the simulation (8 games
each) 3.9 strikes landed per cast; inside the 48-tick windows he took 1235 damage while enemy
champions started 51 actions on him (nearly every hit 1 damage, plus one enemy fountain's 600),
against 1368 and 9 with an 11-tick self-`Banish` after each strike (which blinded his team, section 4)
and 15256 and 62 with `CasterInvisible` alone. `RandomTarget` may pick the same unit again (League's
repeat strikes on one target deal 25%): the bounces deal less than the first strike. Each strike
re-issues `CasterAnimation skill`.

**Channel with its own animation.** `CasterAnimation {name, tick}` + `Delayed` hits +
`RemoveCasterAnimation` at the end (Nocturne ult, Marisa laser).

**A channel that crowd control breaks (league_missfortune R, Bullet Time).** Queued `Delayed` effects run
whatever happens to the caster: a 1 s stun at the sixth of her twelve waves left the other six firing
*(measured in the SDK simulation)*. A test `WithSelf {Stun}` in the ult stunned no one: `WithSelf` applies
its effects to the caster and then again to the action's target unit, and a `Position` cast has no target
unit, so it reaches nobody (the league_janna session's reading of `WithSelfEffect::apply`, 2026-09-28). Death does stop them once
each wave checks a caster buff (`SwitchByBuff bullet_time`; death clears buffs: a death at 156 ticks
ended her waves after 144). For crowd control, each wave first runs `RandomTarget {range: 1,
casting_target: AllyChampionInCC}` whose effects remove that buff and the `CasterAnimation`: range 1 plus
both radii finds the caster herself while she is stunned, rooted, airborne, pulled, feared or charmed
(section 3), so the channel ends at the next wave (at most 15 ticks late); an allied champion in crowd
control standing against her would end it too. The waves are a `Position` cast (the direction is fixed at
the cast, as in League): per wave a `RangeEffect` with `Forward {offset: 1000}` and `DirDot {radius:
100000, range: 906}` (a 50 degree cone toward the cast point; 940, 40 degrees, until 2026-10-01) for the damage
and a view-only `LineRangeProjectile` (100000 x 36000, delay 15, turned to the cast point) for the picture, on
`applied_target: Ally` so that the enemies do not sidestep it (section 8). The cone tests the angle of the
target's centre only, the body's radius counts for the distance alone: "angle <= acos(range / 1000) and distance
from the cone's centre <= radius + both bodies (120000)" matched 99.5% of 23498 logged champion-wave pairs.

**The target and the next one behind it (league_missfortune Q, Double Up).** League's bounce goes to an
enemy behind the first target; `RandomTarget` from the hit point would pick the first target itself again,
and so would a cone (`RangeProjectile` + `DirDot`) placed where a non-penetrating bullet stopped: an area
applies to its units in entity-id order (champions first), not nearest first, and the first target always
stands in it *(measured in the SDK simulation)*. Two `LinearProjectile`s at the same speed (12000) toward
the target, both `penetrate: true`, their applied effects behind caster locks. The narrow visible bullet
(radius 5000) makes the first hit: the first unit it touches takes the shot and adds `q_first` (40 ticks,
the whole flight, so it hits nothing else), `q_window` (7 ticks) and `q_wait` (1 tick). An invisible wide
twin (radius 20000, no view, spawned first) makes the bounce: a unit it touches while `q_window` lasts and
`q_wait` does not takes the bounce and removes `q_window`; before the first hit it does nothing. Without
`q_wait` the twin, overlapping the first target in the tick the window opened, bounced onto it at close
range (12 of 162 bounces); a 2-tick wait also skipped units standing right behind (bounces fell from 65%
to 38% of casts). The first hit carries the kill check (section 7) whose flag outlives the window, and
the bounce's damage waits 4 ticks in a `Delayed` so it can read it: a first shot that killed makes the
bounce crit (double). At speed 7000 the AI sidestepped 15% of the shots (the target walked out of the line
during the 11 ticks of flight); at 12000 every cast hit.
The first version was the narrow bullet alone, penetrating with the 4-tick window: a second unit had to
stand on the bullet's line, and in game Q "never reached a second target" (the user). Over the same six
games that version bounced on 57% of casts but onto a champion 14 times, mostly onto a minion overlapping
the first (median 10600 units apart); the twin bounces on 65%, onto a champion 46 times, median 32000 and
up to 88000 units behind the first target, never onto the first target itself.

**Spin that keeps chasing.** The forced animation holds the caster still (seen in-game: a 3 s
spin with only `can_use_with_move` stood in place), so give every `Delayed` pulse a short dash next
to its `RangeEffect`: `RandomTarget {range: 60000, casting_target: EnemyChampion, effects:
[MoveToTarget {speed: 1400, range: 60000, end_effects: []}]}`. Re-pick the target on every pulse:
chasing only the cast target left Garen spinning in place once it died - at once when it was a
minion. *(Since 2026-10-03 the pulses look in rings instead - a player: "自动吸附敌方英雄有点容易送了，而且清兵的时候
不会动，也很呆": the random champion within 60000 at 1400 a tick dived past the front, and with no champion near he
spun on the spot on 73% of wave and camp spins. Each pulse now dashes at his own move speed (1000) onto an enemy
champion within 25000, else any enemy within 30000, else within 45000 (a 1-tick caster flag skips the outer rings,
league_lucian R's way; `tools/kit/garen_spin.py`): still spins 6%, kill difference within the noise; a version with
no champion ring ended fewer spins alone but lost a kill a game.)* Cast it on `EnemyWithoutTower` so it is also used on waves and camps (on `EnemyChampion`
players never saw it clear and thought it dealt no damage); the pulses' `RandomTarget` still
chases champions in range. See league_garen E.
Once the dashes worked, the user saw Garen chase *without* turning: one 180-tick `CasterAnimation`
issued at the start did not survive the dashes. Base Nightmare plays its forced animation from the
dash's `end_effects`, so league_garen E now re-issues `CasterAnimation spin` on every pulse (after
its `RandomTarget`) and in each `MoveToTarget`'s `end_effects`, each lasting until the next pulse
*(inferred: a dash ending drops the forced animation; not yet confirmed in-game)*.
Make the spin reach past the cast distance. The AI starts an action at `range` plus both units'
radii (league_garen E, range 28000, began with its target about 45 px away, centre to centre), so
a 30000 spin missed whoever stood at its edge and players still called the skill useless, though
it dealt about 70% of Garen's damage *(measured in the SDK simulation)*. League's spin reaches
about 1.9 times Garen's attack range; 40000, with League's +25% on the nearest enemy (here an
`Attack` in each dash's `end_effects`, so the chased champion takes it) and a 6 s armour shred,
took Garen's team from -3.0 to 0.0 kills in 10 minutes against base top laners (240 games). A
position tracker in the simulator must also read `ForceMove` events: dashes do not send
`EntityMove`, and without them the spin looked as if it never moved.

**`MoveToTarget` needs a target.** It dashes to the action's target, so use it in `Targeting`
actions (Nocturne R, Gragas E). Under `casting_type: None` there is none and nothing moves (seen
in-game); LoL Reborn Jax Q wraps it in `RandomTarget {casting_target, range}` instead.

**Multi-hit on random enemies.** Several `Delayed` blocks each holding a `RandomTarget`.

**Projectiles at random enemies.** `RandomTarget {range, casting_target, effects:
[TargetProjectile]}` fires from the caster at the picked unit (LoL Reborn Ezreal E); a
`LinearProjectile` in there flies toward the picked unit too (league_ezreal's W + Q combo). A unit can be
picked more than once. league_ashe W started this way (one arrow at the target plus four random
ones); the user saw homing arrows, not League's cone, so it became the fan above.

**Dash to whoever the skillshot hit (league_leesin Q2).** A projectile's `applied_effects` run
with the hit unit as target, so a `MoveToTarget` there dashes the caster to it (LoL Reborn
Nautilus Q pulls itself in this way). Lee Sin wraps it in `Delayed {tick: 12}` (the mark shows
first) with `Sfx`, the dash and `CasterAnimation q2` inside; the dash's `end_effects` deal the
second hit. The action's `duration` covers wind-up, flight and delay (44 ticks). *(inferred
from the pack; not yet seen in-game)*

**Blink away from a diver or toward a runner (league_ezreal E).** No effect moves the caster part
of the way to a unit: `MoveTo` and `MoveToTarget` in a `Targeting` cast both go all the way, and
`DirTeleport` works only in `Direction` casts. So the E is cast on `EnemyChampionRecentlyAttacked`
(in a fight) with a long `range` and picks its move inside: `RandomTarget {range: 40000,
casting_target: EnemyChampion}` holds `MoveBack` (straight away from that champion: in every hop
measured the AI had aimed the E at the same, nearest one), the bolt at it and a 1-tick flag; without
the flag a second `RandomTarget`
at his attack range decides between staying (only the bolt) and a blink toward the target: an
invisible, non-penetrating `LinearProjectile` on `EnemyChampion` with a 45000 radius and 47500 range,
`end_effects: [Teleport]`, so he lands where it stops, about 48000 short of the first champion it
meets. A projectile checks for units only after its first tick of flight: at speed 20000 it went
20000 units into a champion it already overlapped and dropped him at melee range; at 6000 it
overshoots by at most 6000. `RandomTarget`'s range seems to count both units' radii like an action's
(the hops came with the champion 45000-55000 units away, centre to centre) *(measured in the SDK
simulation, 2026-09-29)*.

**Kick it back into the others (league_leesin R).** `Targeting` on an enemy champion: `Attack` and
`Knockback {speed: 3000, tick: 18}` on the target, plus a `LinearProjectile` toward it with
`penetrate: true` at the same speed (LoL Reborn Nautilus R knocks up along a line this way). The
projectile starts at the caster, a melee range behind the flying target, so it keeps that gap and
hits (`Airborne`, damage) only what the target flies past; its range stops the circle short of the
landing spot. *(inferred: Knockback pushes away from the caster at a constant speed)*

**Get behind him and kick him back (league_leesin R, the insec).** The same kick, but first
`Delayed {7: RushMoveToBack {speed: 8000, applied_effects: []}}`, and the kick keeps its own
`Delayed 17` (the animation's kick frame): Lee flies through the target during the leap and spin and
kicks from behind, so `Knockback` (away from the caster) sends the target back the way Lee came. The
kick can't sit in the rush's `applied_effects`: they fire when Lee touches the target, still in front
of it (far side 5/126); a `Delayed` inside them got behind but the AI then cast R half as often. A
rush from the cast tick at 4500 left Lee behind only 65% of the time (fleeing targets walk
20000-28000 in 19 ticks); starting late and fast aims at a fresh position: behind 337/356, pushed
within 90 degrees of the way back to Lee's start 294/322 (the old forward kick: 1/400, median 176
degrees). The dragon (`LinearProjectile`) waits 4 ticks and flies at 2500 for 35000 so it trails the
target instead of hitting it at once (it still catches it about a third of the time, when the flight
is cut short). R is cast about 20% less often than the forward kick. Balance at lane 1 with the W
below: +0.53 / +0.86 (the old kit -0.96 / -0.58) *(measured in the SDK simulation, 2026-09-29)*.

**Pick the kick: into the ones behind, else the insec (league_leesin R, 0.27.0).** The user wanted both kicks, chosen by
the situation. On the cast tick a hidden probe - a penetrating `LinearProjectile` on `EnemyChampion` (speed 30000,
range 90000, radius 14000; its name is bound to no view, so nothing is drawn) - flies toward the target and counts
the champions on that line with two caster flags (`SwitchByBuff r_one` -> add `r_front`, else add `r_one`; both
removed first, 30 ticks). The target is one, so `r_front` means another champion stands on the line behind it. At
action tick 7 `r_front` runs `MoveToTarget {speed: 8000}` - he stops at the target's front, touching it - and the
kick at tick 17 sends the target into them, the dragon at the kick's speed (3000 for 63000, the old forward kick's)
trailing it from his foot; without the flag the insec above (`RushMoveToBack`, the late slow dragon). A first try
counted with two fixed circles ahead of him (`RangeEffect` at `Forward` 34000 and 66000): the AI casts this
30000-range ult from up to 48700 centre to centre (both bodies count) and the target often flees on (56600 at tick
7), so it sat in both circles, was counted twice and every cast took the forward kick. With the probe 8 of 62 casts
in 17 games kicked forward, knocking up about 1.9 champions each (13 in 7), an insec 0.36 *(SDK simulation,
2026-09-30)*. Lane 1: +0.79 / +0.87, the insec alone +0.53 / +0.86 in the same two batches. league_yasuo's R
beside him: 1.52 a game (the insec alone 1.71) - no change.

**Dash to an ally in trouble and shield both (league_leesin W, Safeguard).** No casting target means
"ally under attack", and all four slots were taken, so W is a check at the end of the attack, Q and E
behind its own caster buff (`league_leesin_w_cd`, 720 ticks, set first in every branch). Three tiers:
a `RandomTarget {AllyChampionInCC}`; then one random ally with 2+ enemy champions near him (a hidden
1-tick `ParabolicProjectile` lobbed onto the ally, its `end_effects` a `RangeProjectile` on
`EnemyChampion` counting with a caster flag, and a `RandomTarget {from_projectile: true}` re-finding the
ally); then any ally with an enemy champion close (a zone that hits a tick later, so tier 2 wins). The
pick shields the ally (a bare `Shield`) and Lee (a self-only `RangeEffect`) on the same tick, then
`MoveToTarget` dashes Lee there; shields in the dash's `end_effects` would be lost to a stun. About 3
dashes a game, 52/53 reach the ally. Checking every ally in one tick with reset zones does not work:
the zones are not processed in spawn order and one enemy was counted by two allies' zones.

**Combos the slots play (league_leesin QQAE, QRQ, RQQ; 0.42.5).** The user wanted League's combos ("QRQ 回旋踢 QQAE RQQ",
no ward hop). The AI casts one slot at a time, so each combo is the slot it spends, shaped by caster flags the slot
before it left:
- Q's casts set `q_cd` (its 360-tick cooldown); Q2 landing with an enemy champion in reach (a `RandomTarget`, range
  12000) adds `q2_on` (150 ticks).
- E cast while `q2_on` holds punches first (QQAE): E branches on `start_timing` 1 - its usual effects wait in a
  `Delayed` 16, still on its tick 17 - so `CasterAnimation attack` replaces E's pose before it shows; the punch (100%
  AD on a champion found by a `RandomTarget`) lands on the attack's hit frame, then `CasterAnimation skill2` and the
  stomp on its frame. Safeguard's check sits once, outside the branch (the game copies `skill` and `skill2` whole
  every tick, so the trees are kept small).
- R cast while `q_cd` holds chases (QRQ): from R's tick 26, `CasterAnimation q2` and `MoveToTarget` 7000 after the
  champion the kick sends off at 3000 a tick - caught in 6-7 ticks - and a 30 + 60% strike.
- R cast with Q ready throws (RQQ): `q_throw` (Q's palm frames alone, a tag cut from the skill strip) on tick 24, then
  a `TargetProjectile` Sonic Wave (8000, `y_offset` 5000: no lift, so its first move does not point the picture up)
  that meets the champion in the air on tick 34, and Q2's dash 8 ticks after the hit.
So every R ends in one of the two. In 12 simulated games: 18 QQAE, 48 QRQ (all caught), 15 RQQ (13 waves hit before
the landing, 12 dashes hit). Against base junglers (lane 1, two batches of 720 games) the kill difference was +0.79 / +0.87 before and +0.58 / +1.21 with the combos (about 10% more damage dealt): the same strength within the noise.
**A flag does not hold every slot.** The first version kept a spent skill's slot behind its cooldown flag (an empty
branch, the hold league_caitlyn W relies on): the AI still cast the held E (`None` on `EnemyWithoutTower`) - 19 times
in 12 games, in fights as well as on camps - and the held ult (`Targeting EnemyChampion`) after every QRQ, each an
empty action that also started the slot's real cooldown. Gating a combo on the slot's level is no easier
(`SwitchByLevel3` is the only level an effect reads; the ult unlocks at 5), so the combos spend no other slot's
cooldown at all.

**Heal an ally at a health cost (league_soraka W).** `Targeting` + `AllyNotSelf`: `Heal
{heal_type: Ally}` on the target, then a 3-tick caster buff with `undying: true` and
`FixedAttack {damage: 0, target_hp_ratio: 6, attack_effect_type: Target}` in a `RangeEffect` on
`AllyOnlySelf` - 6% of her own max health that can never kill her (League forbids the cast below 5%
health). Until 0.15.0 it was a `WithSelf`, and the ally she healed lost 6% of its maximum health too
(section 4). Under
Rejuvenation the cost is skipped and the target gets Rejuvenation too, as in League. *(inferred
from the engine code; not yet seen in game)*

**Heal over time (league_soraka Rejuvenation).** `AddCasted {casted_type: Heal, duration: 150,
period: 30, effects: [Heal {amount: 15, ap_ratio: 6, heal_type: Ally}]}` on the target heals it
5 times (75 + 30% AP over 2.5 s); for the caster itself put it in a `RangeEffect` on `AllyOnlySelf`
with `heal_type: Caster` (the `WithSelf` used until 0.15.0 inside the star's `applied_effects` also hung a
copy on the enemy champion hit, which healed her again while it lived). Every cast adds another instance. *(seen in the SDK simulation: the caster's heal and
self-heal statistics rose with it; not yet seen in game)*

**What a heal is worth to the AI.** Heals score `min(heal, missing health)` (section 3), and the
statistics count only what landed. In simulation a bigger flat heal on league_soraka W (180 ->
320) healed no more in total; a longer range (60000 -> 90000), a shorter cooldown (5 s -> 4 s) and
Rejuvenation passed to the target did (+50% in 10 simulated minutes, near base Priest).

**Heal every allied champion (league_soraka R).** `Targeting` + `AllyChampion` with range 960000
(base Priest's ult range) and `RangeEffect {radius: 960000, target: AllyChampion}` around the
caster. Cast as `None` on `AllyOnlySelf` (Touhou Reimu, LoL Reborn Alistar) the AI fires it as soon
as it is ready, full health or not; a target lets the heal score above (0 at full health) decide.

**Shield the ally beside her, only in a fight (league_janna E, Eye of the Storm with Zephyr).** A
shield scores its full amount on anyone (section 3), so the cast goes on an enemy champion instead:
`Targeting` + `EnemyChampion` (range 90000) fires Zephyr at it (a `TargetProjectile`: damage and a 2 s
slow), then `RandomTarget {range: 50000, casting_target: AllyNotSelf}` from Janna adds a 3-tick lock
buff to her and gives the picked ally the shield, a `WithShield` buff (`attack_mult` 15: the bonus
lasts while the shield holds - 4.0 s on an ally nobody hit, in the simulation) and its view; a
`Delayed {tick: 1}` then checks the lock and, when nobody stood beside her, shields herself through
`RangeEffect {target: AllyOnlySelf}` (a `WithSelf` there would also shield the enemy, section 4). In
10 simulated minutes every cast came in a fight: the shield went 4 times each to the ADC and the mid
laner, once each to top and jungle, and 4 times to herself. `RandomTarget`'s `casting_target` counts
from the caster's team even inside a projectile's `applied_effects`; shielding an ally next to the
enemy the gust hit (`from_projectile: true`, 30000) found nobody most of the time, because she casts
from 85000 away and her lane partner stands beside her.

**Knock them away, then channel a heal (league_janna R, Monsoon).** A `RangeEffect` around her on
`EnemyWithoutTower` with `Knockback {speed: 2000, tick: 15}` pushes every enemy in it straight away from
her *(measured in the simulation: from 28000 to 70000 and from 22000 to 39000 units)*. The channel is a
200-tick caster buff and `CasterAnimation ult_loop` for as long (the forced tag loops, like league_garen's
400 ms spin for 3 s), and four `Delayed` heal pulses 60 ticks apart, each first a
`RandomTarget {range: 1, casting_target: AllyChampionInCC}` that finds only herself, and only while she
is crowd-controlled (it removes the buff and the animation), then `SwitchByBuff` on the buff, which her
death clears as well. Keep every pulse inside the buff: the first draft's fourth pulse came at tick 202
of a 190-tick buff and never healed. Cast on `Targeting AllyChampion` (range 40000, so the heal's score
decides) she used it 3.5 times in 10 minutes, some of them at full health; as `None` on `EnemyChampion`
within 30000 only 1.2 times, and her team did worse (-1.67 against -1.16). Without the knockback the
result hardly changed (-1.25), so it stays: it also sets up league_yasuo's R.
Timing the casts to her animation (attack and Q on tick 13, E on 11, the knockback on 20 instead of 10) took
her from +0.29 to -0.42 against the five base supports; the kit shipped with the storm shield at 150 + 75% AP
and each Monsoon pulse at 130 + 50% AP: +0.11, with league_soraka -0.07, league_leona +0.78 and the base
priest +1.10 in the same batch (either raise alone: -0.20 / -0.15).

**Fold an ability that has its own, longer cooldown into another (league_soraka E on Q).** The
host skill starts with `SwitchByBuff` on a hidden caster buff that lasts the folded ability's
cooldown: without it, cast the full version and add the buff; with it, cast the plain skill.
Soraka's star falls every 8 s, the Equinox field it leaves at most every 16 s (League: 8 s / 16-20 s).

**Once per cast, however many are hit (league_soraka Q's Rejuvenation).** A projectile's
`applied_effects` run once per unit hit; wrap the effect in `SwitchByBuff` on a short hidden caster
"lock" buff that the effect itself adds first, so the second and later hits of the same cast find
the lock. A separate projectile with `applied_target: EnemyChampion` and no view keeps minions from
triggering it.

**Burst where a skillshot stops.** `LinearProjectile {penetrate: false, applied_target:
EnemyChampion}` stops on the first champion; its `end_effects` run where it stopped, so a
`RangeProjectile {delay: 1, apply: 1, shape}` there is the splash (LoL Reborn Jinx R, Fizz R;
league_ashe R). It also fires at the end of the range when nothing was hit.

**Bleed that stacks on the target, threshold counted on the caster (league_darius Hemorrhage).**
Each hit runs `AddCasted {casted_type: Bleed, duration: 300, period: 60}`; every cast adds its own
instance, so the target really carries one bleed per recent hit. What the kit cannot read is how
many the target carries, so Noxian Might counts Darius's own hits instead: hidden caster buffs
`hemo_1`..`hemo_4` (300 ticks each) walked by a `SwitchByBuff` chain checked from the top, the fifth
hit removing them all and adding `might` (`attack_mult`), skipped while `might` runs so it never
stacks. Noxian Guillotine reads the same chain as a ladder of six `FixedAttack`s (+20% per buff,
double under `might`). The chain sits in the basic attack, the empowered attack and Q.
Only champion hits count (the user: minions and monsters must not give Noxian Might): the bleed rides an
invisible twin projectile on `EnemyWithoutTower` (towers take no bleed) and the chain a second one on
`EnemyChampion` (speed 20000, `y_offset` 0; its `applied_effects` run only on a matching target); Q's
chain moved into its `EnemyChampion` `RangeEffect` behind a 6-tick caster lock so a Q through three
champions still counts once. Balance at lane 0 went +0.74 / +1.08 -> +1.33 / +1.30 together with
Apprehend's slow (`AddBuff {move_speed_mult: -40, 60 ticks}` after the `Grab`, about +1.0 on its own)
*(measured in the SDK simulation, 2026-09-29)*.

**Pull a cone to you (league_darius E).** A `Targeting` action whose `RangeEffect` uses
`apply_type {"Forward": {"offset": 1000}}` and `shape {"DirDot": {"radius": 46000, "range": 600}}`
(106 degrees wide, toward the target) and applies `Grab {speed: 3500}` without `tick`, so everyone in
the cone stops at Darius instead of flying past him as a fixed `Pull` would. The sweep is drawn by a
separate `LineRangeProjectile` with empty `applied_effects` (its view turns to the target).

**Hits counted once per cast, heal per champion hit (league_darius Q).** One `RangeEffect` on
`EnemyWithoutTower` for the damage and the bleed, a second one with the same circle on
`EnemyChampion` holding only `Heal {heal_type: Caster}`, so the heal runs once per champion; the
Noxian Might counter sits beside them, outside both, so it counts the cast once.

**Aura that runs while he fights (league_amumu Despair, a League toggle).** There is no toggle and
no periodic aura that follows the caster, so every action (basic attack, each skill, Q on landing)
starts a train unless one runs: `SwitchByBuff train` -> `AddCasterBuff train {tick: 240}` + four
`Delayed` pulses at 0/60/120/180, each a `RangeEffect` around the caster plus a `CasterViewEffect`.
The train buff outlasts the last pulse, so a new train never doubles one; the gap at a restart is at
most one attack. Each pulse checks the train buff again, but a dead Amumu's train buff stays on (his
buffs freeze, section 5), so each pulse first asks `RandomTarget AllyOnlySelf` whether he lives
(2026-10-07; in the game the pulses outlived him otherwise). A sound on the start of a train is gated by its own 600-tick buff.

**A debuff that must not stack (league_amumu's Curse).** Same-name buffs add up (section 5), so a
3 s `damaged_amplify` on every hit would reach +30%. Re-apply it from a pulse with a duration equal
to the period (60 ticks every 60): one instance while the enemy stays in range, gone a second after
it leaves. The ult's longer curse adds a caster "window" buff that the pulses check to skip theirs.

**Pull yourself to the first champion hit (league_amumu Q).** `LinearProjectile {penetrate: false,
applied_target: EnemyChampion}` passes minions and monsters (the AI cannot aim around them); its
`applied_effects` hold the damage and the `Stun`, then a `Delayed {tick: 2}` with `MoveToTarget` and the
`CasterAnimation` for the flight (league_leesin Q2's way). A miss moves nothing. Players never saw it stun ("从来没有
触发过眩晕"; 2026-10-02) while the simulation held 38% of the throws and kept the champion still for 60 ticks, so
the parts no hero proven in the game uses were changed: the dash had sat straight in the `applied_effects`, and
the bandage was the pack's thinnest and slowest (radius 5000, 5000 a tick; then 7000 and 6500: 60% held). Played,
it still missed too often ("的确有点难Q中人", "长度也远一点"): radius 12000, cast range 75000 (was 62000), the
bandage 85000 long (was 70000), the dash 110000 - 73% held in 18 simulated games (56% before; 67% at 10000), and
against base junglers the kill difference went from -0.52 to +0.01 (720 games).

**Third cast is different (league_yasuo Q3).** Two hidden caster buffs count the hits: the first
hit of a cast adds `q_stack`, the next cast's hit swaps it for `q_ready` (both 6 s, one per cast with
the Soraka lock above); the skill starts with `SwitchByBuff q_ready` and fires the whirlwind
(`LinearProjectile`, `penetrate: true`, `Airborne`) instead of the thrust, removing `q_ready`, whose
`view_buffs` entry shows the charged sword meanwhile. Branch at `start_timing` 1 and delay the hits,
so the `CasterAnimation` of the other form replaces the action's animation before it shows.

**A skill that changes shape after another (league_yasuo EQ).** The dash adds a short caster window
buff (40 ticks); the other skill checks it first and strikes as a circle (`RangeEffect` around the
caster) while it lasts. Nothing forces the AI to follow up, but a skill whose target is now in range
and whose cooldown is up is cast as soon as the dash's action ends.

**More of his combos, played by the slots (league_yasuo R Q, Q3 E Q; 0.42.9).** league_leesin's way ("Combos the slots play"): R ends with a lighter EQ circle (EQ's pose and its 25000 cut at 15 + 50% AD, no stack) on its tick 29, after the slash; a champion-only twin of Q3's whirlwind adds `q3_up` (150 ticks - the AI's next E came 85-131 ticks after the knock-up in a simulation, so the knock-up's 60 caught none), and E cast in it cuts the circle 8 ticks into its effects, on the dash (a Q cast during the dash would; Q3 has just been spent) - the same lighter circle. Neither spends Q: at Q's full 30 + 100% with the stack Yasuo's kill difference went from +2.30 to +3.16 (720 games, damage +5%). In 12 games: 33 R Q (every R), 4 Q3 E Q. In mid lane against base mages (two batches of 720 games) the kill difference was +2.30 / +3.16 before and +2.65 / +2.89 with the lighter circles: the same strength.

**A shield that waits for combat (league_yasuo Flow).** There is no "took damage" trigger, so every
action (basic attack, both skills) starts with `SwitchByBuff flow_cd`: without it, add `flow_cd`
(12 s) and the shield on himself through a `RangeEffect` on `AllyOnlySelf` (a bare `Shield` in a
`Targeting` action shields the enemy, and so did the `WithSelf {Shield}` used until 0.15.0, which gave him
nothing when Q, a `Direction` cast, set it off). The first
action of a fight shields him; the ult removes `flow_cd` to refill it.

**A projectile wall does not port (league_yasuo Wind Wall, removed).** Nothing blocks projectiles
(section 4). league_yasuo first stood a picture of the wall in front of him - a view-only
`LineRangeProjectile` (its view turned to the cast direction, so cast upward it lay over his head),
then a 4 s `CasterViewEffect` - with a `RangeEffect` on `AllyChampion` around him adding
`base_attack_damaged_reduce` 40% for 4 s. A wall that blocks nothing read as odd in this game and
the user had the skill removed: leave such skills out rather than drawing them.

**Blink to a crowd-controlled champion (league_yasuo R).** `Targeting` + `EnemyChampionInCC` (range
100000) then `Teleport`; a `RangeEffect` on `EnemyChampionInCC` around the caster re-applies `Airborne`
(the longer time wins) and a `Delayed` second one deals the damage while they are still up.
How often it fires depends on the team's crowd control: in 10 simulated minutes (5v5 on the SDK,
12 seeds) league_yasuo cast it 0.5 times beside base heroes and 2.9 times beside the pack's CC
heroes (Darius E pull, Amumu Q/R stuns, Ashe R, Lux Q root); his own whirlwind mostly lands on
minions, since his Q is cast on anything. **When a new hero brings knock-ups or other hard CC
(Malphite, Alistar, Nautilus...), rerun that simulation with Yasuo on its team and revisit his R**
(its range, or letting it take a few more CC kinds) - the user asked for this.
Supports measured that way (2026-09-28, Yasuo top, the support on his team, 24 seeds a side): he cast it
0.92 times a game beside league_janna (Howling Gale's knock-up, Monsoon's knockback), 1.85 beside
league_leona, 0.54 beside league_soraka and 0.48 beside the base priest - Janna sits between the
supports without hard CC and Leona, and his R stayed as it was. league_morgana (2026-09-29, Dark Binding's
2 s root and Soul Shackles' stun): 1.52 a game, league_janna 0.94 and the base priest 0.65 in the same batch - no
change either. league_riven (2026-09-30, top, Yasuo moved to mid; Broken Wings' third-cast knock-up and Ki Burst's
stun, 24 seeds a side): 2.12 a game with the kit timed to her strips (2.56 before), the base fighter 1.94, the base
knight 0.85, league_malphite 2.42 and league_darius 1.21 on the same seeds - the range the knock-up heroes gave
before (Yone 2.15, Annie 2.19-2.50, the base lightning mage 3.19), so no change.
league_briar (jungle, 2026-09-30, Head Rush's 0.5 s stun, Chilling Scream's 1 s stun, Certain Death's fear): 2.27
a game; league_fiddlesticks 2.81, league_leesin 1.71, league_amumu 1.69, league_ekko 0.90 and the base ninja 0.65
in the same batch - no change.
league_vayne (bottom, 2026-09-30, Condemn's knockback and 1 s stun): 1.75 a game; the base archer 0.65, league_ashe
0.65 and league_lucian 0.44 in the same batch - no change.
league_veigar (mid, 2026-09-30, Event Horizon's cage: a 1 s stun on every champion it catches): 2.40 a game; the base
lightning mage 3.19 and pyromancer 0.65 in the same batch - no change.
league_taric (support, 2026-10-01, Dazzle's 1.25 s stun on a line bursting 0.75 s after the cast, and round a linked
ally): 1.02 a game; league_nami 1.90 and league_leona 1.88 in the same batch - a late-bursting line catches fewer
champions than knock-ups or circles, no change.
league_tristana (bottom, 2026-10-01, Buster Shot's knockback and 0.5 s stun where they land): 1.12 a game;
league_vayne 1.92 and the base archer 0.65 in the same batch - no change.
league_fiora (top, 2026-10-01, Riposte's 1 s stun when the parry blocked a hit): 1.23 a game; the base fighter 1.94
and league_riven 2.42 in the same batch - no change.
league_fizz (mid, 2026-10-01, Chum the Waters' knock-up round the champion the fish stuck to, 2 s after the throw): 1.06 a
game; the base lightning mage 3.19, pyromancer 0.65 and league_veigar 2.44 in the same batch - no change.
league_shaco (jungle, 2026-10-01, Jack In The Box's 1 s fear on champions and the 0.75 s fear of Hallucinate's
three mini boxes): 2.42 a game; league_amumu 1.69, league_leesin 1.52, league_ekko 0.90 and the base ninja 0.65 in
the same batch - fear counts as crowd control, the range the CC junglers gave before, no change.
league_caitlyn (bottom, 2026-10-01, Yordle Snap Trap's 1.25 s root - 1.5 s since - on the first champion to step on it): 0.75 a game;
the base archer 0.65, league_vayne 1.92 and league_tristana 1.08 in the same batch - no change.
league_nocturne (jungle, 2026-10-02, Unspeakable Horror's 1.33 s fear when the tether holds for 2 s): 0.83 a game;
the base ninja 0.65 in the same batch (league_shaco 2.04 and league_leesin 1.52 in an earlier one) - about one
champion a game is still in reach when the tether ends, no change.
league_blitzcrank (support, --lane 4, 2026-10-02, Rocket Grab's 0.67 s stun and Power Fist's 1 s knock-up): 1.98 a
game; league_leona 1.88, league_thresh 1.35 and the base priest 0.65 in the same batch - with the hard-CC supports, no
change.
league_camille (top, 2026-10-02, the E2 dash's 0.75 s stun after a hook on a minion, a monster or a tower; Yasuo mid, his combo kit of #66): 2.17 a game -
the range of the CC heroes before, no change.
league_leblanc (mid, 2026-10-02, Ethereal Chains' 1.5 s root when the chain holds for 1.5 s): 0.58 a game; the
base pyromancer 0.65 and lightning mage 3.19 in the same batch - the root needs the chain to hold, no change.
league_kaisa (bottom, 2026-10-02): no crowd control of her own (her passive's extra Plasma on a crowd-controlled champion
reads her allies' control) - no change.
league_sona (support, --lane 4, 2026-10-02, Crescendo's 1.5 s stun on every champion its wave passes): 1.00 a game;
league_leona 2.19, league_nami 1.94 and the base priest 0.50 in the same batch - no change.
league_kennen (top, 2026-10-02, the third mark's stun: 1.25 s, 0.5 s within 7 s of the last; Yasuo mid): 1.48 a game;
the base fighter 2.33 in the same batch - in the range of the CC heroes before, no change.
league_ryze (mid, --lane 2, 2026-10-03, Rune Prison's 1.25 s root on a Flux'd target; Yasuo top): 1.65 a game;
league_ahri 1.33 and the base lightning mage 3.19 in the same batch - no change.
league_jhin (bottom, --lane 3, 2026-10-03, Deadly Flourish's 1.67 s root on a champion hit lately; Yasuo mid): 1.44 a
game; the base archer 0.50 and gunner 0.19 in the same batch (league_kennen 1.48) - no change.
league_zilean (support, --lane 4, 2026-10-03, the double bomb's 1.25 s stun on every enemy in its blast): 1.40 a game;
league_leona 2.19 and the base priest 0.50 in the same batch - no change.
league_kayn (jungle, --lane 1, 2026-10-04, only the Darkin form's W knocks up for 0.75 s): 1.00 a game; the
base ninja 0.50, league_leesin 1.67, league_vi 2.98, league_amumu 2.83 in the same batch - no change.
league_twistedfate (mid, --lane 2, 2026-10-04, the gold card's 1.67 s stun, thrown only at champions): 1.23 a game;
the base lightning mage 3.19 and pyromancer 0.50 in the same batch (league_ahri 1.27 before) - no change.
league_evelynn (jungle, --lane 1, 2026-10-05, Allure's ripe mark: her next attack charms a champion 1.25 s): 1.81 a
game; the base ninja 0.50 and league_kayn 1.00 in the same batch - no change.
league_sett (top, 2026-10-05, Facebreaker's 1 s stun on two or more pulled in - on one too after his R - cast only with a champion near, and R's stun; Yasuo mid): 1.88 a game; the first kit (Facebreaker on waves too) 2.12, the
base fighter 2.33 and league_darius 1.25 in the same batch - no change.
league_lissandra (mid, --lane 2, 2026-10-05, Ring of Frost's 1.25 s root - also after Glacial Path's blink - and Frozen
Tomb's 1.5 s stun): 1.79 a game; the base lightning mage 3.19 and league_twistedfate 1.23 in the same batch - no change.
league_varus (bottom, --lane 3, 2026-10-05, Chain of Corruption's 2 s root and its 1.5 s spread): 0.71 a game; the base
gunner 0.19 and league_jhin 1.17 in the same batch - no change.
league_alistar (support, --lane 4, 2026-10-05, Pulverize's and Headbutt -> Pulverize's 1 s knock-ups, Trample's 1 s stun):
2.23 a game; league_leona 2.19 and the base priest 0.50 in the same batch - no change.
league_xerath (mid, --lane 2, 2026-10-06, Shocking Orb's 0.75-2 s stun on one unit): 0.94 a game; the base lightning
mage 3.40 and league_lissandra 2.10 in the same batch - no change.
league_brand (mid, --lane 2, 2026-10-06, Sear's 0.83 s stun after Conflagration, W's pillar on the stunned champion):
1.73 a game; the base lightning mage 3.40, pyromancer 0.58 and league_xerath 1.17 in the same batch - no change.
league_viktor (mid, --lane 2, 2026-10-07, Gravity Field's 1.25 s stun after 1.25 s inside, R fired on a crowd-controlled champion):
1.35 a game; the base lightning mage 3.40 and league_brand 1.58 in the same batch - no change.
league_samira (bottom, --lane 3, 2026-10-06, the passive's 0.5 s juggle - only onto a champion already in crowd
control, once every 6 s): 0.25 a game; the base gunner 0.35 and league_varus 0.67 in the same batch - no change.
league_xayah (bottom, --lane 3, 2026-10-08, Bladecaller's 1.25 s root from the third champion hit of one recall): 0.25
a game; the base gunner 0.35 and league_varus 0.67 in the same batch - no change.
league_vladimir (top, 2026-10-08): slows only (Tides of Blood, Sanguine Pool) - not the crowd control R reads, not simulated.
league_rengar (jungle, --lane 1, 2026-10-09, the empowered Bola's 1.75 s root and the leap combo's 1 s root): 1.17 a
game; the base ninja 0.58 and league_khazix 0.35 in the same batch - no change.
league_zed (mid, 2026-10-09): slows only (Shadow Slash) - not the crowd control R reads, not simulated.
league_pyke (support, --lane 4, 2026-10-06, Phantom Undertow's 1 s stun on every champion the phantom passes, Bone
Skewer's pull): 1.88 a game; league_thresh 1.40 and league_leona 2.33 in the same batch - no change.
league_seraphine (support, --lane 4, 2026-10-07, Beat Drop's 0.75 s root from the echoed wave and stun on the crowd-
controlled, Encore's 1.5 s charm): 1.52 a game; league_leona 2.33, league_janna 1.23 and the base priest 0.58 in the
same batch - no change.

**Kill trigger (league_jinx Get Excited!).** No effect fires on a kill, but section 4's facts make one:
1. Next to the damaging projectile, fire an invisible twin with the same speed and path and
   `applied_target: EnemyChampion` (a `TargetProjectile` next to a basic attack's, a
   `TargetSplashProjectile` with the same `range` next to a splash), so only champions are checked.
2. In the twin's `applied_effects`: `AddCasterBuff flag` (a few ticks), an `AddCasted {duration: 3,
   period: 1}` on the target whose effect is `RemoveCasterBuff flag`, and `WithSelf {Delayed {tick: 4,
   SwitchByBuff flag -> reward}}` (the `WithSelf` queues the check twice, on the caster and on the target;
   the first run removes the flag before its reward, so the reward comes once).
3. A living target runs the casted effect and clears the flag; a dead one drops it, and the flag is
   still there when the delayed check reads it.

Where the damage comes a tick later than the hit (league_jinx R until 0.86.12: the blast was a `RangeProjectile`
with `delay: 1` in the rocket's `end_effects`), add the casted effect from a `Delayed {tick: 2}` and read the
flag at tick 7, or it runs before the blast and clears the flag. In 10 simulated games every basic-attack
kill (13) and every rocket kill of the champion it struck (3) was found, and no other hit set it off. Since
0.86.12 the blast comes from a hidden lob a tick after the hit (section 4, "Where a line ends") and its zone hits
a tick after that, so the flag lasts 12 ticks, the casted effect starts at tick 4 and the check reads it at tick 9:
56 of 58 rocket kills found in 240 games (the other two died 7-8 ticks after the hit, after the casted effect had
run: not from the blast).
Rejected on the way: a `RandomTarget` from the hit point after the damage (the dying unit is still
valid that tick), a `Delayed` effect on the target (it runs on the dead), and one twin for all targets
(a minion dying next to an enemy champion set it off). A splash hitting two champions shares one flag,
so a survivor's check can hide the other's death. The same check could build other takedown effects
(Darius's Noxian Guillotine reset).

**A takedown window (league_viego Sovereign's Domination).** League gives Viego a soul when a champion he damaged
dies within 3 s, by anyone's hand. The kill trigger stretched to a window: every champion hit (each slot's
champion-only twin) puts an `AddCasted` (p_win ticks, period 1) on the champion whose effect keeps a 2-tick caster
flag `p_alive` up, and one on him (p_win - 2 ticks) that reads the flag each tick: the flag lapsing inside the window =
that champion died. The latest hit's casted on the champion always outlives his watcher, so a window running out is
never read as a death. Two champions hit in the same window: only the last one to die is seen (the other keeps the
flag up). The add-on (addons/league_viego_soul) reads deaths natively instead and sees each one; its copy of the kit
swaps the casteds for a plain 3-s mark buff on the champion hit.

**Bonus on a new target (league_missfortune Love Tap).** Nothing tells whether an attack's target is the
last one (`SwitchByBuff` reads the caster, and a lasting `AddCasted` marker shows an icon, section 4). What
can be known is when her last target is surely gone: an attack is Love Tap when her previous hit killed
its target (the kill check above on every attack and on Q's first shot sets `lt_ready`) or when she has
not fired for 75 ticks (each attack renews a 75-tick `fight` buff; without it the fight is new). In the
simulation (3 games, 535 attacks) 98 of her 134 target switches came after the old target died, 91 of
those deaths by her own hit; 180 of the 207 attacks after a pause of more than 75 ticks were on a new
target. What the check misses is the AI changing targets while the old one lives (36 of 134). About 55%
of her attacks carry it.

**A trap that waits and snaps once (league_jinx E).** One zone cannot last and hit once (section 4), so
the trap is 20 short links (15 ticks each, 5 s). They were a chain - each link's hidden `ParabolicProjectile` started
the next from its `end_effects` unless a lock on Jinx was on - and a chain started from `end_effects` goes on after
the caster dies (below): players saw champions bitten again and again ("夹子反复触发", then "被秒的英雄同时碰到了两个
炸弹" on a version that only kept the dead caster's checks from spawning). Now the links are flat, league_teemo R's
way: a `Position` cast keeps its point for every effect it runs, so each link is a `Delayed` of the cast itself (the
throw lands on tick 36, the links follow every 15 ticks, the fizzle after them), and the SDK stops a dying caster's
pending `Delayed` effects - in simulation the chain showed 19 links after Jinx's 7 deaths with a trap out, the flat
links none after 6. The game does not stop them (section 5, league_riven R); there the heartbeat below ends the trap.
Each link, at the cast point:
- skips if this trap already bit (`e_spent<slot>`, set a tick after the bite): one bite per trap;
- from the third link on, skips unless the link before it ran (`e_hb<slot>_<k-1>`, set by that link): the links go
  on after her death in the game, and a dead Jinx cannot add the heartbeat, so the trap stops one link later (two
  if she dies before the second link), one bite at most. The 2026-10-07 audit kept it so rather than ask
  `RandomTarget AllyOnlySelf` in all 40 links: that cost 200 effect nodes on the pack's biggest skill2 tree, which
  the game copies every tick (docs/perf.md);
- shows the lying trap and, unless a trap bit someone in the last 90 ticks (`e_lock`, shared, the root's length),
  starts the check: a `RangeProjectile` (`delay` 14, `apply` 1) on `EnemyChampion` whose effects bite every champion
  inside (`Bind` 90, damage, a `ViewEffect`) and `WithSelf {Delayed {tick: 1}}` set `e_lock` and `e_spent<slot>`.
Casts alternate between two slots (a `Permanent` toggle), so a second trap thrown while the first lies (cooldown
cuts) has flags of its own; each cast clears its slot's. The first link is not gated by the heartbeat, so the AI,
which scores the branch the caster's buffs pick, still sees the bite: 176 throws in 12 simulated games (169 before),
69% bit a champion (63%), no champion bitten twice within 90 ticks, none after her death. The throw lands on the cast
point itself (`range` 120000), where the links stand.

**A trap that lasts, with three at once (league_teemo Noxious Trap).** Links nested in each other's
`end_effects` (league_jinx E until 2026-10-02) cannot run long: that file was 119 levels deep, and serde_json stops at
128, so the chain could not run much past its 20 links (5 s). A `Position` cast keeps its cast point for
every effect it runs, `Delayed` ones included (league_soraka's Equinox; every `RangeProjectile` and
`ViewEffect` of league_teemo R appeared on the mushroom's spot in the simulation), so the links can sit
side by side in the ult's own `Combine` (19 levels deep, 292 KB for three mushrooms of 12 s):
- the throw: a `ParabolicProjectile` with only a view (20 ticks), then the arming `ViewEffect` at tick 20;
- at tick 80, a `RangePeriodProjectile` trigger (radius 8000, `period` 1, the mushroom's life) whose
  applied effect, while the caster has `alive`, swaps `alive` for a `boom` flag; and a
  `RangePeriodProjectile` damage zone (radius 30000, `period` 2) whose applied effect, while `fire` is on,
  poisons and slows and puts `fire` out a tick later - every unit in the cloud is hit on that one
  application, and the next one comes after `fire` is gone;
- a picture link every 15 ticks: `SwitchByBuff alive` -> the lying mushroom (a 250 ms view), else
  `SwitchByBuff boom` -> drop `boom`, light `fire` (3 ticks), play the cloud's view and its sound. The
  burst comes at most a quarter second after the trigger.

Flags on the caster are shared by every copy of the cast, so three mushrooms at once need three slots:
the cast takes the first slot whose `busy` buff (the whole life) is gone and uses that slot's `alive`,
`boom` and `fire`. `busy` must outlast every pending link of its mushroom, or a new mushroom in the slot
would wake the old one's links; with charges of 20 s a slot comes back after its third throw at the
earliest, so a 12 s life is safe even with a third off the cooldown. When the caster dies his buffs go
and the mushrooms with them (death clears buffs, section 5); League's last for minutes and outlive
Teemo. In simulation 5 of 6 mushrooms burst, most within a second or two of arming.

**Weapon picked by distance (league_jinx Switcheroo!).** The attack's `range` is the long weapon's
(rockets, 64500). At `start_timing: 1` a `RandomTarget {range: 52500, casting_target:
EnemyWithoutTower}` adds a 2-tick `near` caster buff; `SwitchByBuff near` fires the minigun (its own
attack-speed stacks) or plays `CasterAnimation rocket` and fires rockets. A permanent `fishbones` buff
remembers the gun in hand, so the swap sound plays only on a change and the rockets' -10% attack
speed lasts until the next minigun shot. Simulated: 70% minigun, 29% rockets, a swap every ~3.6
attacks.

**A rocket that bursts where it lands, with splash.** `TargetSplashProjectile` hits early (section 4)
and a projectile cannot start a zone from its hit, so league_jinx fires three together at one speed:
the visible `TargetProjectile` (its hit plays the explosion), a hidden `TargetSplashProjectile` for
the damage and the hidden champion twin of the kill trigger.

**Every fourth spell stuns, and only champions use it up (league_annie Pyromania).** Hidden permanent
caster buffs `pyro_1`..`pyro_3` count casts, walked from the top like the Darius chain; the fourth
removes them and adds `pyro_ready` (and a 3 s glow buff with a `view_buffs` entry, refreshed - removed
and added again - by every action while the stun is ready, so the glow stays on while she fights and
is gone within 3 s of her death). Q and R count one cast each; skill2 is W with E folded in and counts
two (a second counter call guarded by `SwitchByBuff pyro_ready`, so W can make the stun ready and E
then adds nothing). Three rules keep it League's:
- the cast decides: `SwitchByBuff pyro_ready` at cast time picks the stunning version, so the fourth
  cast's own fireball does not stun even though `pyro_ready` is on when it lands;
- only champions use it up: the stunning version fires the normal damage plus a hidden twin on
  `EnemyChampion` (a `TargetProjectile`, a `RangeEffect` cone, a `RangeProjectile` circle) whose effects
  are `Stun`, the stars and `WithSelf {Delayed {tick: 1, RemoveCasterBuff pyro_ready}}` - every champion
  the cast reaches on that tick is stunned before the buff goes, and a fireball on a minion keeps it
  (the AI throws Q at whatever is in range; League's players save the stun for champions);
- it is back after death: every action first checks a `Permanent` `pyro_init` flag, and without it adds
  the flag and `pyro_ready` (death clears buffs, section 5).
In 10 simulated minutes she stunned 14 champions; a Q, W or R cast in flight when the next spell starts
could carry a second stun, but each of her actions lasts longer than its projectile's flight.

**A shield that burns back (league_annie Molten Shield, folded into W).** A `Shield` on her through a
`RangeEffect` on `AllyOnlySelf` (until 0.15.0 a `WithSelf {Shield}`, which shielded the enemy W was cast on
as well) followed by `AddCasterBuff` of a `WithShield`
buff with `damage_reflect` 20 (and its `view_buffs` picture): the reflect and the picture end when the
shield breaks or runs out (section 5). League's E returns a flat hit once per attacker; the engine only
has the percentage. `damage_reflect` sends that share of every hit the unit takes - basic attacks and
skills alike - back to whoever dealt it on the same tick, as `BaseAttack` physical damage *(seen in the
SDK simulation from the `Damaged` events, with 30: while shielded she took 57 / 93 / 127 (a skill) /
192 / 308 and her attackers 17 / 27 / 38 / 57 / 92 on those ticks)*. Lowering it from 30% to 20% (with
Q's ratio at League's 75%) took her team from +1.83 to +1.42 kills over 10 simulated minutes.

**A summon that follows its target and burns (league_annie Tibbers).** Summons cannot walk or attack in
data, so Tibbers is a `Targeting` cast on an enemy champion whose pictures and burns ride on that champion
(section 4's facts on `Targeting` zones, `AddCasted` and dead targets):
- the drop: the 400 ms drop picture as a `ViewEffect` (`is_follow`) at the cast, and at tick 5 a hidden
  one-tick `ParabolicProjectile` whose `end_effects` start the damage circle (and the Pyromania twin on
  `EnemyChampion`) round the target's spot, hitting at tick 6 on the picture's impact frame;
- his stay: at tick 24 an `AddCasted` (`Fire`, duration 301, period 60) on the target, six runs 60 ticks
  apart, each playing his ring and 1 s standing loop (`ViewEffect`s with `is_follow`, so they walk with the
  target), his swipe (`TargetSfx`) and a one-tick lob that starts the burn circle round the target; the
  target's death clears it, so he stops with the target;
- his end: a second `AddCasted` (duration 384, period 383) added at the cast runs at ticks 1 and 384 and
  plays the vanishing puff once a 10-tick start flag is gone - only if the target lived;
- a death he leaves at: a tick before each second's boundary a `Delayed` effect adds a 2-tick caster flag,
  which the engine skips once the target is dead; at the boundary a missing flag means the target died in
  the last second, and the puff plays there, once (a flag refreshed at every living boundary allows it).
Annie's death does not end him - a casted effect goes on without its caster, as League's Tibbers outlives
her - but a dead caster cannot lob, so the stay's burn checks a caster flag her death clears and then burns
the target alone. A `ViewEffect` is not turned like a projectile's view, so an upright bear can stand in
it. The pictures go under the units (`z` -1, the ring -2), the bear 9 px behind the target so the target
stays in front of him: a view on a unit may be mirrored with the unit's facing like a `CasterViewEffect`
*(inferred)*, and behind it he would only turn round, where beside it he would jump from side to side.
Up to 0.13.0 he was a `Position` cast that stood where he landed, and targets walked out of his ring.

**A shield that comes back after it breaks (league_malphite Granite Shield).** League's shield returns after
10 s without taking damage; nothing reads "not damaged", but a `WithShield` buff says whether a shield still
holds (section 5). Every action (attack, both skills, the ult) starts with the same `SwitchByBuff` ladder:
- the `granite` buff (duration `WithShield`) is there: the shield holds, nothing to do;
- no `granite_init` flag (`Permanent`, cleared by death): the first action of a life shields him at once and
  adds the flag;
- `granite_cd` (600 ticks) is running: it is recharging;
- a `granite_wait` flag (`Permanent`) is there: the timer ran out - shield him again, drop the flag;
- otherwise the shield just broke: start `granite_cd` and set `granite_wait`.
The shield itself is a `RangeEffect {Circle 1000, AllyOnlySelf}` holding `Shield {amount 60, ap_ratio 60,
tick 36000}` (a `Shield` has no `hp_ratio`; 60 + 60% AP tracks League's 10% of max health over the levels),
added before `granite` so the `WithShield` buff finds it. `granite` also carries `defence_mult` (Thunderclap's
armour, higher while the shield holds) and its `view_buffs` picture, both gone the tick the shield breaks
*(measured in the SDK simulation: shield 104 at level 1, broken, the 10 s timer started at his next action,
shielded again at the first action after it)*. So the shield returns 10 s after it broke rather than after 10
s unhurt: in a long fight it comes back about every 10 s.

**Charge onto a champion and knock up where you land (league_malphite R).** `Targeting` on `EnemyChampion`:
a 60-tick `cc_immune` caster buff (unstoppable), `CasterAnimation` of the charge, and `MoveToTarget {speed:
4000}` whose `end_effects` play the landing (`CasterAnimation ult_slam`) and, after a `Delayed` of 4 ticks
(the strip's impact frame), the crater (`CasterViewEffect`, not turned), the sound and a `RangeEffect` around
the caster (radius 30000, plus both units' radii) with the damage and `Airborne`. A `Position` cast would land
on the spot the target left; homing puts every knock-up on the chosen champion, and whoever stands near him
goes up too. The landing takes 5-27 ticks depending on the distance, so the slam comes from the dash's end
rather than from the action's own animation.

**Out and back (league_ekko Q, Timewinder).** A `Direction` cast fires a penetrating `LinearProjectile` (the
device); its `end_effects` play the field's picture (a `ViewEffect` on the stop point, unturned), start the slow
zone there and, in a `Delayed` as long as the field lasts, a `BackToCasterLinearProjectile` that flies from the
stop point back to Ekko and hits everything on the way home (section 4). Both passes hit every unit they touch;
the first unit of each pass also counts a Z-Drive Resonance hit behind a 30-tick caster lock per pass (the
Soraka "once per cast" lock). League's device stops on the first champion and expands there; this one always
flies its full range first.

**A sphere that bursts once the caster steps in (league_ekko W, Parallel Convergence folded into E).** A
hidden `ParabolicProjectile` with `travel_time` 90 is lobbed at an enemy champion (a `RandomTarget` on
`EnemyChampion` within 60000 picks it, so camps never spend the 14 s cooldown); its `range_effect_name` is the
forming rings on the landing point, and its `end_effects` start three zones there: a check zone (`period` 1,
`AllyChampion`) whose `RandomTarget {AllyOnlySelf, from_projectile: true}` finds Ekko only inside the sphere
(section 4) and then sets a `done` lock, a 3-tick `boom` flag and the shield; a slow zone (`period` 10, a
10-tick slow while `done` is off); and a stun zone (`period` 1) that stuns every enemy in it while `boom` is on
and removes `boom` a tick later. The picture is a chain of `Delayed` `ViewEffect`s in the same `end_effects`:
a 250 ms dome every 15 ticks until `done`, and a check every tick that plays the shatter once. In the
simulation (14 games) 73% of the spheres burst, most on their first tick, because Ekko has just dived onto
their target; a radius of 40000 instead of 30000 stunned 2.3 champions a game instead of 1.4.

**Back to where he stood (league_ekko R, Chronobreak).** Nothing remembers a unit's past position, so the
anchor is dropped at the cast and the rewind comes 4 s later: a `LinearProjectile` with `speed` 1, `range` 1
and `y_offset` 5000 (a linear projectile otherwise starts 5000 above the caster's feet; the 永恩 session
measured it for Yone's E) ends the tick it appears, its `end_effects` hold the cast position, and a `Delayed
{tick: 239}` there runs `Teleport` (to that position), a 20-tick `damaged_reduce` 100 / `cc_immune` buff, the
arrival animation, the heal and a `RangeEffect` around him (now the arrival point). The pending rewind checks
a 250-tick caster buff first, so death (which clears buffs) cancels it. The hologram left at the anchor is a
`CasterViewEffect` without `is_follow`, played at the cast. In the simulation every rewind landed on the cast
position to the unit (jumps of 30000 to 216000 units - TFM2 heroes walk a quarter of the map in 4 s); the
blast caught about 0.3 champions a cast whatever its range, radius or delay, so the ult is worth its heal and
its escape.

**Z-Drive Resonance with a rest and the ult counting (league_ekko).** The user asked for League's rule: R's
blast counts a Z-Drive hit and the passive has a cooldown. League's is 5 s per target, but `SwitchByBuff`
reads only the caster's buffs, so the rest is a caster buff (`league_ekko_z_cd`) started on every proc and
checked before every ladder (attack, both passes of Q, E): while it runs no hit adds a stack. R's blast adds
one stack (two `RangeEffect`s, champion first, behind a 2-tick `r_zlock`). A 5 s caster-wide rest cost too
much (lane 1: +0.82 / +0.09 -> -0.29 / -0.35, and a bigger proc did not win it back: 140 -0.24 / -0.24, 170
-0.81 / -0.25); 3 s with the proc at 100 AP came closest (+0.12 / -0.23), 2 s with 110 about the same (+0.16 /
-0.29), so the kit uses 180 ticks *(measured in the SDK simulation, 2026-09-29)*.

**Combos on the ult only (league_yone Q3 R, R Q3; 0.42.9).** His Q and W trees are the pack's largest (371 and 659 nodes) and the game copies skill and skill2 whole every tick, so the combos sit in R: a champion-only twin of Q3's wave adds `q3_up` (90 ticks), R cast in it skips the 15-tick wind-up (Q3's dash pose, the same slash on tick 8), and a champion-only twin of R's hit line gives Q's stack (`q_lock` keeps it one per cast), so the Q after an R is Q3 more often. In 6 games 3 of 31 Rs were quick (R, on a 50 s cooldown, was ready at about a third of the Q3 hits on champions), and 15 Rs left the storm ready (2 before). In mid lane against base mages (720 games) the kill difference was +2.20 before and +2.20 with the combos.

**Leave the body, fight as a spirit, snap back (league_yone E, Soul Unbound folded into W).** Every 15 s (a
caster cooldown buff), when a `RandomTarget` finds an enemy champion within 50000 (it sets a 2-tick flag the
next `SwitchByBuff` reads), W opens with Soul Unbound; otherwise it is a plain W. The body stays: Ekko's anchor
(a `LinearProjectile` with `speed` 1, `range` 1, `y_offset` 5000) plays the body left behind in its
`end_effects` - a `ViewEffect` bound to the sprite's own `e_body` tag (League's `Spell3_bodyLoop`, 2 x 2000 ms,
`z` 0, not following) - and 239 ticks later pulls him back with `Teleport` if the spirit buff is still there
(death clears it). The spirit (a caster buff with `move_speed_mult` 25 and a `view_buffs` aura) dashes onto a
champion (`RandomTarget` + `MoveToTarget`) and cleaves there.
League repeats a share of the damage dealt meanwhile; nothing reads the damage dealt, so every damaging hit
has a champion-only twin (the attack's `TargetProjectile`, twins of Q's, Q3's and R's lines, W's champion cone)
that, in spirit form, queues a `FixedAttack` of 25% of that hit's own numbers. The pop must land after the
return, whenever the hit came: the cast adds a ladder of caster buffs (b1..b11, 20, 40 ... 220 ticks) and a
binary search of `SwitchByBuff` over them finds the first still present, the hit's 20-tick bucket k; the pop
is a `Delayed` of 240 - 20k + 2 ticks, landing 2-22 ticks after the return, and pops only while `e_back`
is on, a 30-tick caster flag the return's `Delayed` adds: a dead Yone cannot add it, so no echo pops once he died.
Until 2026-10-07 the pops read `e_alive`, added at the cast for 272 ticks, which a dead Yone's frozen buffs kept on - in
the game every queued echo still popped. (A search guard on each of the 108 echoes cost 6 effect nodes apiece, skill2
465 -> about 680; the flag costs one. In the SDK 12 games blocked 9 echoes, all while he was dead, and 145 popped; the AI
no longer sees an echo before the return, so the games part from the old ones.) The mark on the enemy is an `AddBuff`
on the target
with that same wait as its duration and a `ThreePhase` picture (intro, loop, a dimmed last frame): in the
simulation it came on with the hit and went off the tick before the burst. Two engine facts from it *(seen in
the SDK simulation)*: a `Delayed` `FixedAttack` on a unit Yone's team could not see (its `EntityIsVisible` for
his team false - it had walked into the fog) dealt no damage, so an echo is lost on a champion that fled out
of sight; and `Shield` effects add up - W's champion cone holds a `Shield` through a `RangeEffect` on
`AllyOnlySelf` (a `WithSelf` would shield the target too, section 4), and two champions hit gave two shields
at once, with the picture and sound once per cast behind a 3-tick caster lock. Eight twins with twelve leaves
each make the kit 325 KB (league_jinx and league_teemo are as large).

**Hook the first champion and drag him in (league_thresh Q, Death Sentence, with W folded in).** A
`Direction` cast on `EnemyChampion` fires a `LinearProjectile {penetrate: false, applied_target:
EnemyChampion}` (it flies through minions) whose `applied_effects` hold the damage, a 60-tick `Stun` and a
`Grab {speed: 1500}` with no `tick`: the stunned champion is dragged all the way to him (section 4, "Pull vs
Grab"). Its `end_effects` start a `BackToCasterLinearProjectile` at the drag's speed for the hook coming back
(on a miss it comes back from the end of its range). League's recast that flies Thresh to the target is left
out. Dark Passage rides on the same cast behind its own 840-tick caster cooldown buff (`SwitchByBuff`, as in
"Fold an ability that has its own, longer cooldown into another"): a `Shield` on him through a `RangeEffect`
on `AllyOnlySelf`, and a `RandomTarget {casting_target: AllyNotSelf, range: 50000}` throwing the lantern (a
`TargetProjectile` whose `applied_effects` shield that ally). League's lantern that pulls the ally who clicks
it cannot be built.

**A prison that hurts only the first champion in it (league_thresh R, The Box).** League's five walls cannot
be placed round him (`Line` takes map coordinates, section 4), so the Box is one circle: an
`ApplyInProjectile {follow_caster: false, tick: 300, shape: Circle 40000, applied_target: EnemyChampion}`
started from Ekko's anchor (a `LinearProjectile` with `speed` 1, `range` 1, its `end_effects` on the spot he
stands); the picture is a `CasterViewEffect` in the cast itself (`z` -1, not following) - as a `ViewEffect` in
the anchor's `end_effects` it never showed in game (section 4). The zone hits each champion once, whenever he
touches it (section 4). Its `applied_effects` are a `SwitchByBuff` on a caster buff `r_broken`: without it,
the champion gets the damage, the 99% slow for 120 ticks, and `AddCasterBuff r_broken` (330 ticks, longer
than the zone); with it, only a 60-tick slow. The cast removes `r_broken` first, so every Box starts whole.

**Stages at levels 5, 8 and 12 (league_kayle Divine Ascent).** Nothing reads a level but `SwitchByLevel3`, so
her maximum health is the level table (900 + 95 a level): a 3-tick `Shield` of S on herself (a `RangeEffect`
`AllyOnlySelf`), a `WithShield` flag, then `FixedAttack {hp_ratio: 10}` on herself - 10% of her maximum health
breaks the shield only from the level whose health passes 10 x S (S = 123, 151, 189: halfway between two
levels), and 2 ticks later `SwitchByBuff` on the flag gives the stage (a `Permanent` caster buff: range, the
fire wave, Transcendent's speed). Absorbed, the hit costs no health; a 2-tick `undying` guards the rest. Before
it, a `WithShield` flag added with no shield of her own says an ally's shield is on her (it would hold the
flag): skip and try later. After it, a 100 shield against a 99 `FixedAttack` must break - any damage
amplification would fake a level. Each life's first action re-reads the stages silently (death cleared them),
then an action at most every 2 s tries the next one, with the ascent's picture and voice. In 12 simulated
games no stage came early; they came 2-4 s after the level-up (median).

**An ult that waits for danger (league_kayle R, Divine Judgment).** League gives the invulnerability to whoever
is about to die; nothing in a mod reads current health (section 3 "Which ally gets an ally skill"), so the rule
the user picked uses the danger the data can see: an allied champion in crowd control within 50000 gets it at
once (`RandomTarget` `AllyChampionInCC`), else Kayle herself when two or more enemy champions stand within 30000
of her, else nothing. Two engine facts shape it *(SDK simulation, 2026-09-29)*:
- The AI picks an ult slot cast on `EnemyChampion` while it closes in (the nearest enemy champion 60000 or more
  away at 78 of 87 casts, mostly 60000-100000), seldom once the fight is on. A 3-tick check cast in the slot itself, refunded when
  nobody needed it, ran about every second on the approach and found nobody in 10 minutes. So the slot only
  arms the ult: a 3-tick action on the `idle` tag adds a 900-tick `r_armed` caster buff, and every attack, Q and
  E runs the check while it lasts (her attacks keep coming all fight). A save removes `r_armed` (on the same
  tick for an ally, so a check a tick later cannot save a second one), forces `CasterAnimation ult` for 44 ticks
  and plays the voice; an unused window ends with a 3-tick `ult_cooldown_mult` buff that caps the cooldown at
  60 ticks (section 5), and the AI arms it again on the next approach.
- Counting enemies: a `RangeEffect` on `EnemyChampion` round her whose per-target effect is
  `SwitchByBuff n1 ? AddCasterBuff n2 : AddCasterBuff n1` (3-tick flags) leaves `n2` on her from the second
  enemy on - a buff added for one target of a `RangeEffect` is seen by the next target's `SwitchByBuff` on the
  same tick. A `Delayed {tick: 1}` then reads `n2`.
Against this pack's crowd-controlling heroes the ult went out 1-3 times a game, the receiver at 66% health on
average (the old "an enemy champion in range: a crowd-controlled ally or herself" went 68 times of 71 to Kayle
herself, at 93%); against base teams, with little crowd control, less than once. It made her stronger in the
balance runs (+1.03 / +1.78 against +0.84 / +1.12 with the same numbers): the old ult spent itself on a full-health
Kayle as each fight began. Her Q and E went back from 70 / 50 to 60 / 40 damage: +0.89 / +1.30.

**Push or pull by the situation (league_thresh E, Flay).** League lets the player sweep either way; the AI
needs a rule, checked on the hit tick (a `Delayed` in the cast): within 2 s of a hook (a caster buff the hook's
`applied_effects` add) it pulls - the hooked champion is dragged next to him and a pull throws him through and
behind, League's hook-and-flay; otherwise a `RandomTarget {range: 16000, casting_target: EnemyChampion}` sets a
2-tick caster flag when a champion is right on him, and `SwitchByBuff` on that flag picks the push
(`Knockback {speed: 2500, tick: 12}`) over the pull (`Pull` with the same numbers) in a `RangeEffect` around
him. `RandomTarget`'s range also counts the target's body, so "right on him" reaches about 28000 between the
centres (a champion pushed from 28550 in the simulation); minions and monsters, with no champion near, are
pulled together. The first version pulled 1500 x 10 (15000): the user could not see Flay do anything.

**Frighten on the first hit out of combat (league_fiddlesticks A Harmless Scarecrow).** League's passive places
an effigy; nothing placed can act here, so the scarecrow is Fiddlesticks himself standing still. Every action
first runs `SwitchByBuff fight` with an empty branch for the buff and, without it, `AddCasterBuff ambush` (40
ticks), then replaces `fight` (`RemoveCasterBuff` + a 180-tick `AddCasterBuff`: one instance, section 5). The
attack fires a champion-only twin of its bolt (`TargetProjectile` on `EnemyChampion`) and Reap a champion-only
circle beside its damage; both hold `SwitchByBuff ambush` -> `Fear` (60 ticks), its picture and sound and the
flag's removal a tick later, so every champion reached on that tick is frightened first. In the simulation he
mostly opens with Terrify, which outranges both, so the passive fires rarely (one of 18 champion fears in a
sampled game).

**Double damage on a champion already in crowd control (league_fiddlesticks Q, Terrify).** League doubles
Terrify on a target already feared. Two `TargetProjectile`s leave together at the same speed: the crow on
`EnemyWithoutTower` (damage, picture, sound and a `Delayed 1 {Fear 75, the fear picture}`) and a twin on
`EnemyChampionInCC` holding a second copy of the damage. A projectile's `applied_target` is tested when it
hits, not at the cast *(measured with a probe kit in the SDK simulation: of five casts on stunned champions all
five dealt the damage twice, of five on free ones none did)*, and the crow's own fear waits a tick so that the
twin, hitting on the same tick, never counts it. Any of the six crowd-control states of section 3 doubles it
(a stun, a knock-up, a root, a fear...), not only fear.

**Strike, then drain everyone around him (league_fiddlesticks skill2: Reap with Bountiful Harvest).** A
`Position` cast on `EnemyWithoutTower` (range 40000). Three `RangeProjectile`s on the cast point with the same
`delay` 24 and `apply` 6 (the hit 5 ticks after they appear, section 4): Reap's damage and 40% slow on
`EnemyWithoutTower` in 30000, the passive's fear on `EnemyChampion` in 30000, and `BlockSkill` (75 ticks, the
silence) with its picture on `EnemyChampion` in a 14000 core. Twelve ticks later the channel: a caster buff for
its length and `CasterAnimation w_loop` (120 ticks), then eight `Delayed` pulses 15 ticks apart, each first
running the crowd-control check of "A channel that crowd control breaks" and then `SwitchByBuff` on the channel
buff: a `CasterViewEffect` (the souls round him), a `RangeEffect` (40000) on `EnemyWithoutTower` with the
damage, a small `Heal {heal_type: Caster}` and the drained-soul picture - every unit drained heals him - and one
on `EnemyChampion` with a larger heal for each champion. League's tethers that break when a target walks away
are left out: the drain reaches whoever stands within 40000 at each pulse.

**A tether picture on a range drain (league_fiddlesticks W, the soul chain).** Players missed League's tethers
("w吸血看不到链条", 2026-09-30), so every pulse also sends each drained unit a link: a hidden `TargetProjectile` (speed
100000) at the unit, a hidden `ParabolicProjectile {travel_time: 1}` from its hit onto the unit's spot, and from that
lob's `end_effects` a `BackToCasterLinearProjectile` (`w_chain`: 1600 a tick, radius 0, no effects) flying from the
unit back to him. The same `BackToCasterLinearProjectile` placed straight in the `TargetProjectile`'s
`applied_effects` never appeared (0 of 119 in a 5-minute SDK game): it starts only from a projectile's end, as
league_nami W's return and league_ekko Q's. Each link flew exactly distance / 1600 ticks and went on reaching him.
Links 24 px long (Codex drew the chain at game size) and 1600 x 15 ticks = 24000 apart make one continuous chain; `z`
1 draws them over the units - under them (-1) a foe standing next to him hid nearly all of it. The drain itself is
unchanged: still by range, no tether to walk out of.

**Channel, vanish in crows, land in a storm (league_fiddlesticks R, Crowstorm).** A `Position` cast on
`EnemyChampion` (range 80000, `start_timing` 1): a caster buff `r_ch` (61 ticks), `CasterAnimation ult` (60),
the landing mark as a `ViewEffect` (a `Position` cast plays it on the cast point, `z` -1), and at ticks 15, 30
and 45 the crowd-control check removing `r_ch` and the animation. At tick 60 a `SwitchByBuff r_ch` does the
rest only if the channel held: a `CasterViewEffect` of the burst of crows where he stands (not following, so it
stays behind), `Teleport` (to the cast point), `CasterAnimation ult_land` (30) and a 302-tick `storm` buff. Ten
`Delayed` pulses 30 ticks apart each run `SwitchByBuff storm`: the circling crows (`CasterViewEffect`,
following) and a `RangeEffect` (45000) of damage; the first also fears the champions around him for 60 ticks.
Death clears the storm buff (section 5), so the storm ends with him.

**Out and back, the return true damage (league_ahri Q, Orb of Deception).** Ekko's out and back without the
field: the penetrating `LinearProjectile` on `EnemyWithoutTower` turns into a `BackToCasterLinearProjectile`
in its `end_effects` at once. Each hit of the return starts with `AddCasterBuff` of a 1-tick
`magic_resistance_penetration: 100` buff, then the `ApAttack` (section 4, "True damage that scales with
ability power"). A buff laid on at the turn for the whole flight home (30 ticks) worked too, but also let
the fox-fires hitting meanwhile through magic resistance. The hit sound plays once a pass (a 30-tick lock).

**Fox-fires, charmed champions first (league_ahri W, folded into Q).** Q starts with `SwitchByBuff` on a
9 s cooldown buff (Soraka's fold); without it W adds the buff, two move speed buffs (+20% for 1.5 s and +20%
for 0.75 s: 40% decaying) and a caster picture of the fires circling her, and queues three fires 4 ticks
apart. Each fire picks in tiers: `RandomTarget {casting_target: EnemyChampionInCC}` fires a
`TargetProjectile` at a crowd-controlled champion (the charmed one, or anyone's stun) and adds a 1-tick
caster flag; `SwitchByBuff` on the flag skips the next tier, `RandomTarget {EnemyChampion}` (the same way), and
last `RandomTarget {EnemyWithoutTower}`. One flag name per fire, so two fires in one tick cannot see each
other's. In the simulation the fires went to minions in the lane and to the champion as soon as one stood
within 60000 (all three onto the same champion when he was the only one: `RandomTarget` may repeat).

**Three dashes with bolts (league_ahri R, Spirit Rush).** The ult has `cooltime_use_count: 3` (section 7,
"Recast / charges"): cast on an enemy champion within range, the AI casts it again as soon as the action
ends, so the three dashes came within about 1.5 s in the simulation, and one charge returns every
`cooltime / 3`. Each cast first sets a 1-tick flag with `RandomTarget {EnemyChampion}` at a short range and
branches: with a champion that close, `MoveBack` (away from the target, speed x tick); otherwise
`RushTime` in the `Targeting` cast, which moves speed x tick toward the target (2000 x 12 = 24000, measured)
and stops there - unlike `MoveTo` and `MoveToTarget`, which go all the way to the target (section 4). After
the dash a `Delayed` fires three bolts, each a `TargetProjectile` from a `RandomTarget` on `EnemyChampion`,
else on `EnemyWithoutTower` (the flag tiers above). The dash's picture is a `CasterViewEffect` left where she
started (not following), drawn round rather than pointing, since she dashes either way.

**Heal on the hits of every fourth spell (league_ahri Essence Theft).** League's old passive (nine spell
hits, then the next spell heals per enemy hit) as casts: each spell's hits count the cast once behind a
per-skill caster lock (Q 60 ticks, the fires 60, E 40, each R dash 24) on permanent caster buffs `et1`,
`et2`, and the third adds `et_ready` (permanent, with a `view_buffs` picture; death clears it, section 5). Every
spell starts with `SwitchByBuff et_ready`: it swaps the flag for a heal window (`et_heal`, as long as the
spell's hits come: Q 80 ticks, E 40, R 40), and while the window lasts each hit runs `Heal {heal_type:
Caster}` instead of counting (the heal picture and sound once, behind a 20-tick lock). A Q through a wave
heals once per unit it passes on each pass, as League's did.

**Two shots after a spell, the second weaker on champions (league_lucian Lightslinger).** Every spell adds a
180-tick caster charge (Q and R `ls_1`; E+W, two spells, `ls_1` and `ls_2`). The attack (`start_timing` 1) runs
`SwitchByBuff ls_2` -> remove it and fire the double, else `SwitchByBuff ls_1` -> the same, else the single shot
(`Delayed` to tick 7). The double plays its own animation (`CasterAnimation passive`, 26 ticks, as long as the
attack) and fires on ticks 6 and 13. League's second shot deals less to champions only; beside it flies a
champion-only twin (`TargetProjectile` on `EnemyChampion`, the same speed and `y_offset`, so both land on one
tick) that gives the caster a 2-tick flag, and the real shot deals 50% at once and, `Delayed 1`, the other 50%
unless the flag is there - minions and monsters take both halves *(inferred from league_ezreal Q's measured
twin: the order two projectiles land in within a tick does not matter)*. Make it seen: the user found no
double shot in game while the simulation had 45 a game - both bullets left one point on one line 7 ticks
apart. Each now leaves the pistol that fires it in the double-shot animation (a `TargetProjectile`'s
`y_offset` lifts only its picture: -21000 for the upper one, -7000 for the lower; -15000 and -4000 on the
first model) as a thick tracer, blue
then gold, bigger than the plain attack's bullet (a gold light on the pistols while a charge waited was
tried and rejected: "我只要被动的两发子弹看起来明显就行了"). `y_offset` did move a bullet's arrival by a
tick in the simulation, so it is not purely a picture setting.

**Bonus on the next two attacks when a champion near him is crowd-controlled (league_lucian Vigilance).**
League's Vigilance follows an ally's immobilising; nothing tells who applied a state, so any counts. The attack's
first effect is `RandomTarget {range: 60000, casting_target: EnemyChampionInCC}` -> `SwitchByBuff vig_lock`
(nothing) else a 90-tick lock, two 240-tick charges and the glow on his hands (a caster buff with a view). Each
shot then spends one charge (`vig_b` first) on a hidden `TargetProjectile` beside it carrying the `FixedAttack`
and the spark picture, so the arming attack is the first of the two.

**Dash away, hop back or chase into range (league_lucian E, Relentless Pursuit, with W folded in).** League's E
goes wherever the player clicks. One `Targeting` action on `EnemyWithoutTower` (range 80000) picks by the
situation, league_ezreal E's way with three branches: `RandomTarget {range: 30000, casting_target:
EnemyChampion}` holds a 1-tick flag, `CasterAnimation skill2_back` (31 ticks) and `MoveBack {speed: 6000, tick:
5}` (away from that champion); without the flag a `RandomTarget` at his attack range (55000) on
`EnemyWithoutTower` sets a second flag that chooses a hop (`skill2_back`, `MoveBack` 5000 x 3) over the chase:
an invisible non-penetrating `LinearProjectile` on `EnemyWithoutTower` (speed 6000, range 30000, radius 40000,
`end_effects: [Teleport]`) that drops him about 40000 short of the first enemy it meets. The chase keeps the
action's own animation (`skill2`, League's forward `Spell2`). Ardent Blaze is `Delayed` to tick 14 and leaves
from wherever he landed. In 12 simulated games: 95 chases (50 cast at champions), 162 hops, 4 dashes away
*(SDK simulation, 2026-09-29)*.

**Hits speed him up while the mark lasts (league_lucian W, Ardent Blaze).** The bolt's burst (`RangeProjectile`
in its `end_effects`) marks what it hits (`AddBuff` with the picture, 6 s) and gives the caster a 6-s flag. Every
hit's `applied_effects` (the attack's bullets, Q's beam) run `SwitchByBuff` on the flag -> `RemoveCasterBuff` and
`AddCasterBuff` of a 60-tick `move_speed_mult` 25 (one instance, refreshed). League speeds him up only for hits on
the marked enemy; nothing reads a buff on the target, so here any hit counts.

**Shots at the nearest champion, through minions (league_lucian R, The Culling).** League sprays one aimed
direction and minions block it. `RandomTarget` picks at random among the units in its range, so each of the 20
`Delayed` shots (9 ticks apart from tick 10, each first running the crowd-control check and `SwitchByBuff` on the
channel buff) tries rings: `RandomTarget {range: 40000, casting_target: EnemyChampion}` sets a 1-tick flag and
fires; without the flag the same at 75000, then 110000; nothing further, no shot. The bullet is a
non-penetrating `LinearProjectile` on `EnemyChampion` toward the picked champion: it flies through minions and
stops on the first champion. Of its shots 58% hit at speed 8000 and 85% at 12000, the champions walking out of
the line *(SDK simulation, 2026-09-29)*.
Its picture is not on that line: a `LinearProjectile` starts 5 px over the caster's pivot, at his pivot's x, with
the tracer's nose on it and its tail behind, so for two or three ticks the shot streaked from his back across his
hips (the user: "卢锡安开大时子弹不是从枪口里射出去的"). The line is now `league_lucian_r_line` (no view, unseen) and
beside it, in the same effects, flies a `TargetProjectile` with the picture (`league_lucian_r_bullet`: the same
speed and target, no `applied_effects`), lifted 8 px (`y_offset` -3000). It flies at the target's pivot, so a
lifted picture slopes down onto it (league_caitlyn: 16.5 px sloped 12 degrees, "子弹看起来是歪的"): lifted to the
barrels' middles (11 and 14 px) it dived 15-19 degrees into a champion 40 px away; at 8 px the tracer's top rows
leave the lower barrel, 6.5 degrees at 70 px and 11 at 40. Level and at the barrels needs the ult frames' pistols
lower. Its view starts with an empty tick (the lift
jump, see "A beam from a raised weapon") and then shows only what has left the muzzles 20 px ahead (4 and 16 px,
`import_lucian.py` `R_IN`), and plays once. In the simulation each line spawned its twin on the same tick (the
twin at the caster's own spot, the line 5000 north), the twin arrived 2 ticks after the line's hit (inside the
120 ms hit spark), and 85% of the shots hit before and after *(SDK simulation, 2026-10-01)*.

**Every third hit deals true damage, the max-health part on champions only (league_vayne Silver Bolts).** League
counts three hits in a row on one target; nothing tells which unit a hit is on (see "Bonus on a new target"), so her
own hits count - the attack's bolt, the Tumble bolt and Condemn - on two 210-tick caster stacks (league_ekko's
Z-Drive ladder, run in each bolt's `applied_effects`, so only hits count). The third deals a flat `FixedAttack` on
whatever it hit and leaves a 2-tick caster flag; the bolt's champion-only twin (also the kill check's twin, below)
reads the flag in a `Delayed {tick: 1}` and adds `FixedAttack {target_hp_ratio: 6}`, so minions and monsters take
only the flat part (League caps the bolts on monsters, and the epic monster has 10000 health and more). Measured: the
flat 40 on the bolt's tick and 6% of a priest's maximum health (54) a tick later, the percentage never on minions
*(SDK simulation, 2026-09-30)*. Condemn's bolt flies only at champions, so its ladder carries both parts itself.

**Tumble by the situation, the next attack stronger (league_vayne Q, Tumble).** league_lucian E's three ways with a
roll in place of the blink: `MoveBack` (6000 x 5) away from a champion within 30000, a hop back (5000 x 6) when
anything is within her attack range, else `RushTime` (3000 x 10, `penetrate`, no applied effects) toward the target -
a fixed distance, where `MoveTo` would run onto the unit. A 420-tick caster buff turns the next attack into a stronger
bolt; League's auto-attack reset is not there (the attack's own cooldown runs on). Hopping back costs her attacks: a
15000 hop gave -0.6 kills against none (12 seeds a variant) and the first version kept a 10000 hop (24000 away, 25000
forward); players found the dash too short ("vn的位移太短了", 2026-09-30) - the in-range hop is the one they see most - so
all three are 30000 now (League's 300 against her 550 range): +2.15 / +2.08 against +2.57 / +2.39 before in the same
batches, the hop often leaving her out of range to walk back in.
While Final Hour runs each Tumble adds `CasterInvisible {tick: 60}`.

**Knock back, then stun where it lands (league_vayne E, Condemn).** A `TargetProjectile` on `EnemyChampion` whose hit
deals the damage and `Knockback {speed: 3000, tick: 8}`; inside a projectile's `applied_effects` it pushes straight
away from the caster (measured: 66439 to 102434 units off in 12 ticks at 3000 a tick). A `Delayed` as long as the
knockback deals the slam and the stun wherever the target landed - League's wall, which TFM2 does not have, so it
always comes. A long knockback costs her damage: at 36000 the target flew out of her 55000 attack range and her next
attack came a median 77 ticks after the cast; 24000 gave +1.2 kills (12 seeds).

**A steroid that her kills refresh (league_vayne R, Final Hour).** A `None` cast on `EnemyChampion` (range 60000):
an 8 s caster buff with `attack_mult` 25 and `skill_cooldown_mult` 100 (both skills: no field speeds one skill
alone), read by Tumble for the invisibility, by Night Hunter for the triple speed and by the attack for Final Hour's
shot sound. League adds 4 s per takedown; here the kill check (see "Kill trigger") runs on every champion hit of hers
while the buff lasts and removes and re-adds it, back to 8 s (one instance, so the stats never double). For a hit
from a `Delayed` on the target (Condemn's slam) the clearing `AddCasted` is added one tick later from a `Delayed
{tick: 1}` and the flag read at 5 ticks. Assists cannot be seen. In a simulated game both refreshes came 4 ticks
after her hit killed a champion, one of them a Silver Bolts proc *(SDK simulation, 2026-09-30)*.

**Root the first champion, hurt everything on the way, at a champion when one is in reach (league_morgana Q,
Dark Binding, with W folded in).** A `Direction` cast on `EnemyWithoutTower` (range 80000), so it also goes to
waves and camps. Two `LinearProjectile`s on one path at one speed: an invisible penetrating one on
`EnemyWithoutTower` whose hit (damage, a small picture) is skipped under a caster flag `q_bound`, and the visible
orb, `penetrate: false` on `EnemyChampion` (it flies through minions and monsters), whose hit binds (`Bind` 120),
heals her (Soul Siphon, a `Heal {heal_type: Caster}` of a share of the damage) and adds `q_bound` from a `Delayed
{tick: 1}` - the orb and the damage hit the bound champion on the same tick, and from the next one nothing behind
him is hurt. The cast removes `q_bound` first. W's pool sits in the orb's `end_effects` (where it stopped): a
`Delayed {tick: 2}` checks `q_bound` (no pool when nothing was bound) and W's own 12 s caster cooldown, then starts
two `RangePeriodProjectile`s (the damage on `EnemyWithoutTower`, a heal-only twin on `EnemyChampion`) and the
pool's picture as a `ViewEffect` on the point. Two engine facts *(SDK simulation, 2026-09-29)*:
- **A slow skillshot is dodged.** Champions move about 1000 units a tick and sidestep: a bind orb at 3500 a tick
  (League's slow Q) bound a champion on 10% of 102 casts, 6000 and 8000 on about 25%, 10000 on 36% (three games
  each).
- **Aim at a champion, cast at anything.** The AI casts a `Direction` skill on `EnemyWithoutTower` at whatever unit
  it picked, in lane mostly a minion. The orbs therefore sit twice in the cast: inside a `RandomTarget {range:
  75000, casting_target: EnemyChampion}` (whose effects also add a 1-tick `q_aim` flag), where a `LinearProjectile`
  flies toward the picked champion, and in a `SwitchByBuff q_aim` that fires them the cast's way only when no
  champion was in reach. The picked champion must be inside the orb's reach (75000 plus the radii against a range of
  80000). With both, 38% of her Qs bound a champion (13-21 a game) and the first draft's -2.96 kills became -1.04.

**Crowd-control immunity for an ally (league_morgana E, Black Shield).** league_janna E's pattern (cast on an enemy
champion, the shield to a random `AllyNotSelf` within 50000, herself when nobody stands beside her) with
`AddBuff {duration: "WithShield", cc_immune: true}` next to the `Shield` (150 + 70% AP, 300 ticks; a `Shield`
takes every kind of damage, where League's Black Shield takes only magic). A `cc_immune` buff given to another
unit works like the caster's own *(SDK simulation, a probe counting the `Stun` / `Bind` / `Airborne` / `Knockback` /
`Pull` / `Grab` / `Fear` / `Charm` events on champions holding the buff, 2026-09-29)*: in three games 1 crowd-control
event landed on a champion under Black Shield (about 15,600 champion-ticks with it), against 538-606 a game on all
champions.

**A hook a crowd-control shield stops (league_thresh Q against league_morgana E; Blitzcrank's Rocket Grab later).**
The hook's `Stun` and `Grab` are blocked by `cc_immune` *(SDK simulation, 2026-09-30: a probe on every hook end,
Morgana and Thresh on opposite sides, 48 games: 0 of 23 hooks on a champion under Black Shield stunned or dragged,
against 244 and 217 of 309 hook ends near an unshielded one)*. Everything else in the hook's `applied_effects` is no
crowd control and still lands: the chain-wrap picture played on 18 of the 23, and the `q_hooked` caster flag that
turns Flay into a pull was set 18 times. So what should follow only a landed hook rides an invisible twin fired right
after it (same speed, range, shape and path, no view, `penetrate: false`) with `applied_target: EnemyChampionInCC`:
it hits the hooked champion in the same tick once the hook's stun holds, and passes a shielded one. With the twin
carrying the flag and the picture: 0 of 22 on shielded champions, 262 of 332 otherwise. A grab built from `Grab` /
`Pull` / `Stun` is stopped by the shield for free; one built from `MoveToTarget` or `Teleport` on the target is not.

**Tethers that break out of reach and snap after 3 s (league_morgana R, Soul Shackles).** A `Targeting` cast on
`EnemyChampion` (range 45000): a `RangeEffect` (radius 50000) on `EnemyChampion` round her deals the damage and heals
her; she gets 20% move speed for 3 s. Each champion it reaches gets a tether of its own, a chain of pulses written
out nine deep in that `RangeEffect`'s effects: a 21-tick 20% slow whose `view_buffs` picture is the chain, then a
`Delayed {tick: 20}` firing a hidden `TargetProjectile` (speed 100000, no view) from her at the champion, whose
`applied_effects` run `RandomTarget {range: 84000, casting_target: AllyOnlySelf, from_projectile: true}` -> a 1-tick
caster flag, `SwitchByBuff` on it -> the next pulse (the ninth: the damage again, a 90-tick `Stun` and the snap's
picture), and `RemoveCasterBuff` for the next champion's check. One check out of reach and that champion's tether is
over - no more slow, no stun - as in League, where it breaks at 1050 against a 625 cast radius (84000 = 1.68 x
50000). The check measures from the projectile's hit point to her, and both bodies add about 18000 (with range 70000
a tether held at 86137 and broke at 90877). The same `RandomTarget` in a plain `Delayed` on the champion never finds
her (every check failed, one at 9287). A `TargetProjectile` inside a `Delayed` in another one's `applied_effects`
does spawn (nine levels here). Her death ends the tethers: in the SDK no pulse spawns from a dead caster; in the game
the pulse flies, but its `AllyOnlySelf` check finds no dead caster. Until 0.25.0's review
a single `Delayed {tick: 180}` `RangeEffect` (70000) stunned every enemy champion near her then, also one that had
run off and come back or had never been chained (the user: "脱离了大招的线就不应该眩晕了吧"). In 16 simulated games
62 champions were chained: about 36 died within the 3 s, 12-19 ran out of reach and 0-3 were stunned, at check
ranges of 60000 to 105000 alike - a champion walks about 1.2 cast radii a second here, against 0.56 in League.

**Three charges, the third cast different (league_riven Q, Broken Wings).** `cooltime_use_count: 3` with cooltime 720
(a charge back every 4 s). The casts count themselves, not their hits: the first adds a 240-tick `q_1` caster window,
a cast during it swaps `q_1` for `q_2`, a cast during `q_2` removes it and leaps (League's 4 s recast window; left
unused the chain starts over). Every cast hops onto its target (`MoveToTarget`) and slashes round her on arrival; the
third knocks up round where she lands. The AI weaves the charges with basic attacks by itself - Q, attack, Q, attack,
Q (about 70 casts a game in the SDK simulation), so each rune a cast gives is spent at once, as in League.

**Runes the next attacks spend (league_riven Runic Blade).** Every spell adds a rune, at most three: caster buffs
`rune_1`..`rune_3` of 360 ticks, and each gain removes all three and adds them again up to the new count, so they run
out together as in League (separate timers would leave `rune_2` without `rune_1`); a buff added in a tick is seen by a
`SwitchByBuff` later in the same tick, so E+W's two gains count two. The attack spends the highest rune for its bonus.

**A self-buff ult armed on the way, started at the fight (league_riven R, Blade of the Exile).** The AI casts an ult
slot on `EnemyChampion` while it closes in (league_kayle): cast as a plain buff, Riven's R went off with the nearest
enemy champion 45000-110000 away and the 15 s often ran out on the walk (4 casts, 1 Wind Slash in a game). The slot is
now a 3-tick action on the idle tag (`None` on `EnemyChampion`) that adds a 600-tick `r_armed` caster buff and starts
the R at once when a `RandomTarget EnemyChampion` finds one within 35000 (44 of 45 casts in 12 games), else at her
first attack with a champion that close; left unused, a 3-tick `ult_cooldown_mult` 4900 caps the cooldown at 60 ticks.
Wind Slash, the recast, fires by itself: a 900-tick ready flag and a 300-tick wait; after the wait her attacks and a
train of `Delayed` checks every 30 ticks from the cast fire it (`RandomTarget EnemyChampion` within 60000 -> a
`LinearProjectile` toward the picked champion, 70000 long; the damage adds `target_hp_ratio` since nothing reads
missing health). Per game over 12 seeds: 3.5 starts, 2.0 slashes, 1.7 champion hits; with the checks in her attacks
only, 1.3 slashes; with a 90000 reach 1.9 slashes but 0.9 champion hits (the wave fell short of far champions).
After the cast most fights were over within 5 s (she often walked off), which is why the wait is kept short of the
buff and the checks run on their own.

**The weapon reforged while the ult lasts (league_riven R, the user's option B).** The engine plays `idle` and `run`
by itself, so they cannot change with a buff; every action can. Her strips that show the sword have `_r` twins with
the reforged blade (`attack_r`, `skill_r`, `q2_r`, `q3_r`, `skill2_r`; the ult and Wind Slash, which only happen
inside R, were redrawn in place), and each action picks one by `SwitchByBuff league_riven_r`: Q and E+W in their
`CasterAnimation`, the basic attack at `start_timing` 1 (`CasterAnimation attack_r` or nothing) with its hit in a
`Delayed` to tick 11, where it landed before (league_yone's second slash is picked the same way). While she stands
or walks the broken blade shows, under an aura bound to the same buff (`view_buffs`, z -1). Her E shield shows as
a `ThreePhase` picture on an `AddBuff` of duration `WithShield` next to the `Shield` (league_morgana's E), and the
runes as one `view_buffs` glyph each on `rune_1`..`rune_3`, so as many glyphs light over her head as she holds.

**A stream that bounces enemy - ally - enemy (league_nami W, Ebb and Flow, with E Tidecaller's Blessing folded in).**
Every projectile leaves from the caster, whatever starts it *(SDK simulation, 2026-09-30: the spawn events' x and y)*:
a `LinearProjectile`, `TargetProjectile` or `ParabolicProjectile` started in another projectile's `end_effects`, or in
a `RandomTarget` there, left from where Nami stood, not from the stop point. Only a `BackToCasterLinearProjectile` in
plain `end_effects` leaves from the point (league_ekko Q), and it flies back to the caster (inside a `RandomTarget`
it was not spawned at all). So no stream can fly from one champion to the next; the bounce is searches round the hit
points and pictures on the units, 9 ticks apart:
- the stream: a `Targeting` cast on `EnemyWithoutTower` (range 60000) fires a `TargetProjectile` at an enemy champion
  in reach (`RandomTarget {EnemyChampion}` with a 1-tick `w_aim` flag, league_morgana Q's aim), else at the cast target;
- its hit: the damage and the Blessing's slow, then `RandomTarget {from_projectile: true, range: 50000, casting_target:
  AllyNotSelf}` - a search round the unit hit - whose effects set a 3-tick `w_other` flag, heal and bless that ally in
  a `Delayed {tick: 9}` (its heal picture is the bounce) and lob a hidden `ParabolicProjectile` at it (`travel_time` 8,
  from a `Delayed {tick: 1}`: a projectile placed straight in `applied_effects` never spawns) whose `end_effects`
  look for the last target round the ally's spot;
- nobody else there (`SwitchByBuff w_other` finds no flag): a hidden `ParabolicProjectile` with `travel_time` 1 lands
  on the unit hit, its `end_effects` check that Nami stands within 50000 of it (`RandomTarget {AllyOnlySelf,
  from_projectile: true}` -> a 2-tick flag) and start a `BackToCasterLinearProjectile` there, the stream visibly
  flying back to her; its `end_effects`, run on her when it arrives, heal her (`Heal {heal_type: Caster}`), bless her
  (a `RangeEffect` on `AllyOnlySelf`) and look for the last target round her.
Nothing marks a unit already hit, and the ally was found next to the first target, so a plain `RandomTarget
{EnemyChampion}` round the ally picked the first target again for 9.5 of the 10.5 last hits a game (a search radius
of 15000 instead of 50000 still 1.8 of 2.5). The last hit therefore counts first: a champion-only twin of the stream
(`applied_target: EnemyChampion`, the same speed) sets a `w_t1c` flag when the first target is a champion, a
`RangeProjectile` (`delay` 2, `apply` 1) on `EnemyChampion` round the hop's landing spot counts with the Kayle flags
`w_n1` / `w_n2`, and a second hop (`travel_time` 2, the same spot) reads them: after a champion the last hit needs two
enemy champions there, after a minion or a monster one. Then 0.5 last hits a game fell on the first target and 1.3
on another champion *(6 simulated games each)*. League's Blessing empowers the ally's next three attacks and spells
and their hits slow; nothing runs on another unit's attacks, so here it is `attack_mult` and `magic_power_mult` 15 on
the healed ally for 4 s, and the slow rides on W's own damage hits.

**A bubble lobbed at a champion in reach (league_nami Q, Aqua Prison).** A `Position` cast on `EnemyWithoutTower`
(range 70000) with league_morgana Q's aim: a `RandomTarget {EnemyChampion}` throws the bubble at a champion in reach
and sets a 1-tick flag, else it goes to the cast point. The bubble is a `ParabolicProjectile` (`travel_time` 24; its
`range_effect_name` is the landing ring, shown for the whole flight) whose `end_effects` play the burst on the point
and start a `RangeProjectile` (`delay` 1, `apply` 1, radius 22000) with the damage, `Airborne` 75 (League's
suspension; crowd control for `EnemyChampionInCC`) and the prison picture on each unit (`is_follow`). In the
simulation 39% of her Qs caught a champion, 1.45 champions each.

**A wave whose slow grows with the distance it rolled (league_nami R, Tidal Wave).** A `Direction` cast on
`EnemyChampion` (range 90000): a caster buff `r_near` for 32 ticks and a penetrating `LinearProjectile` (speed 2500,
range 160000, radius 32000, `y_offset` 5000 so it rolls from her feet) whose hits deal the damage, `Airborne` 30 and a
60% slow for 120 ticks while `r_near` lasts, 180 after it (League's slow grows from 2 to 4 s with the distance). A
wave of radius 26000 caught 1.1 champions a cast, 32000 about 1.6 (League's wave is as wide as an attack range);
faster waves did not catch more. An invisible twin on the same path with `applied_target: AllyChampion` gives every
ally it passes the passive's haste twice over (League doubles Surging Tides for allies the wave touches); it passes
Nami as it starts, so she gets it too.

**A bleed that heals the caster, one stack a second from attacks (league_briar Crimson Curse).** Every hit runs
`AddCasted {casted_type: Bleed, duration: 301, period: 60}` whose effects are the damage (`Attack` 2 + 3% attack) and
`Heal {amount: 1, attack_ratio: 1, heal_type: Caster}`: a caster heal inside a casted's periodic effects heals the
unit that applied it, on every tick of every instance *(SDK simulation, 2026-09-30)*, so each stack heals her
six times over its 5 s. League's heal grows as she loses health and every ability costs 5% of her current health;
nothing reads current health, both are dropped. The basic attack adds a stack only when a 60-tick caster lock is
off (`SwitchByBuff bleed_lock` -> nothing, else the lock and the bleed), so one target carries about five of hers,
League's cap; the skills always add one.

**Leap, stun, then a frenzy whose first attack after 2 s is a heal bite (league_briar Head Rush with Blood Frenzy
and Snack Attack).** A `Targeting` cast on `EnemyWithoutTower` (range 47500) so it also opens camps: a `RandomTarget
{range: 47500, casting_target: EnemyChampion}` leaps at a champion in reach and adds a 1-tick `q_aim` flag, and
`SwitchByBuff q_aim` leaps at the cast target only when no champion was found (league_morgana Q's aim). The leap is
`CasterAnimation` + `MoveToTarget {speed: 3500}` whose `end_effects` hit, `Stun` 30, cut armour and magic resist
(`AddBuff {defence_mult: -10, magic_resistance_mult: -10}`, 300 ticks), add a bleed and start the frenzy: remove and
add the `frenzy` caster buff (300 ticks, `attack_speed_mult` 40, `move_speed_mult` 20, one instance) and restart the
Snack timer (remove `snack_done` and `snack_wait`, add `snack_wait` for 120 ticks). The basic attack switches on
`hema` (the ult's frenzy), then on `frenzy`: inside either, `SwitchByBuff snack_wait` -> a frenzied hit, else
`SwitchByBuff snack_done` -> a frenzied hit, else Snack Attack (`Attack {damage: 30, attack_ratio: 130,
target_hp_ratio: 4}`, a caster heal, and `snack_done` for the rest of the frenzy). A frenzied hit is `Attack` 60% on
the target plus a `RangeEffect` (circle 16000 at `Forward {offset: 18000}`, `EnemyWithoutTower`) of 40%: the target
stands in the circle, so it takes the full 100% and whoever is next to it the splash. League recasts W for the bite;
nothing here can press it, so it is the first attack 2 s into each frenzy.

**Charge behind a shell, then a cone that knocks back and stuns champions (league_briar E, Chilling Scream).** A
`Targeting` cast on `EnemyWithoutTower` (range 40000, 80 ticks): `CasterAnimation skill2` for the 60-tick charge, an
`e_guard` caster buff (`damaged_reduce` 15, 60 ticks, its `view_buffs` picture the shell) and four `Delayed` heals on
her alone (`RangeEffect` + `AllyOnlySelf`); `Delayed {tick: 60}` plays `skill2_scream`, and 4 ticks later the scream:
a view-only `LineRangeProjectile` (no effects, its picture the sound wave) and two `RangeEffect`s at `Forward
{offset: 1000}` with `DirDot {radius: 50000, range: 800}` (37 degrees each side) - on `EnemyWithoutTower` the damage,
an 80% slow for 30 ticks, `Knockback {speed: 2500, tick: 16}` (40000) and a bleed; on `EnemyChampion` a `Delayed
{tick: 16}` `Stun` 60, so the stun starts when the knockback ends. League stuns only against a wall; there are no
walls, so every champion knocked back counts as hitting one (the user's pick).

**Kick at the first champion, fly to it, fear the others (league_briar R, Certain Death).** A `Direction` cast on
`EnemyChampion` (range 120000): after 8 ticks a `LinearProjectile {penetrate: false, applied_target: EnemyChampion,
speed: 9000, range: 130000}` (it flies through minions and monsters) whose hit marks the prey (a 420-tick buff with
the mark picture), gives her a 60-tick `cc_immune` caster buff, plays `ult_fly` and runs `MoveToTarget {speed:
5000}` - in a projectile's `applied_effects` it flies the caster to that projectile's target (league_leesin Q2). Its
`end_effects` are the landing: `ult_land`, the blast picture, then `AddBuff {cc_immune: true}` for 2 ticks on the
prey, a `RangeEffect` (35000) of damage and bleed on `EnemyWithoutTower` and a `RangeEffect` (40000) of `Fear` 90 on
`EnemyWithoutTower`: the fear is blocked on the prey by the buff given just before it, the damage is not - League's
"fears every enemy but the prey" *(SDK simulation, 2026-09-30: the prey never feared, the others near her were)*.
Then Hemomania, the frenzy of Head Rush with more attack and move speed plus `defence` 20, `magic_resistance` 20
and `vamp` 10, for 360 ticks. League's range is global and the frenzy lasts until she or the prey dies; with the
AI casting it on any champion in range a global kick would send her alone across the map, so it reaches a bit
more than a screen and lasts 6 s (the user's pick).
**Hidden for a fixed time on landing, armed as she casts (league_akali W, Twilight Shroud folded into E).** E (every
8 s) runs W behind W's own 18 s caster cooldown buff (Soraka's fold), armed at the cast: `RandomTarget {range: 40000,
casting_target: EnemyChampion}` adds a flag buff that lasts past the landing (`MoveBack` 7 ticks + 2), and a
`Delayed` 7 on landing fires only under that flag (`SwitchByBuff`, the flag removed): the smoke as a `CasterViewEffect`
(not following: it stays where she landed - a `ViewEffect` on her own spot would not show, league_thresh R), a plain
`CasterInvisible {tick: 120}` in the effect list, and the decaying move-speed buffs. Checking on landing instead missed
the champion she was fighting: the flip puts her 21000 further back (24000 + 21000 > 40000). In the simulation W went
off 3-6 times a 10-minute game and each `EntityInvisibled` window lasted 1.98 s, over the dash back.
The first build folded W into Q as a zone, hidden only while she stood inside - still a working way to tie
invisibility to an area: Ekko's anchor (a `LinearProjectile` with `speed` 1, `range` 1, `y_offset` 5000) whose
`end_effects` start a `RangePeriodProjectile` (radius 30000, 300 ticks, `period` 6, `applied_target: AllyChampion`)
applying `RandomTarget {range: 30000, casting_target: AllyOnlySelf, from_projectile: true}` -> `CasterInvisible {tick:
8}`: each pulse renews it while she is inside, it ends at most 8 ticks after she steps out (and flickers at the edge).
The user moved W to E; there she leaves the cloud 0.5 s later on the dash, so a fixed duration fits.

**Flip back, throw, dash to what the throw hit (league_akali E, Shuriken Flip).** A `Targeting` cast on
`EnemyWithoutTower`: `MoveBack {speed: 5000, tick: 4}` (20000 straight away from the target), then from a
`Delayed {tick: 4}` - so it leaves from where she landed - a non-penetrating `LinearProjectile` at the target that
stops on the first unit. Its `applied_effects`: the damage, the mark (`AddBuff` whose `view_buffs` entry is the
shuriken on the unit, as long as the wait), a `Delayed {tick: 1}` champion-only `TargetProjectile` (the passive and
the ult's counter count champions only; aimed at a minion it is removed the tick it spawns without applying), and
`Delayed {tick: 30}` with the dash: the crowd-control check of "A channel that crowd control breaks" (no dash while
she is stunned), `CasterAnimation skill2_dash`, `MoveToTarget` (6000 a tick) and the second hit in its
`end_effects` (league_leesin Q2). A unit that died meanwhile gets no dash (a `Delayed` on a dead unit only plays its
pictures and sounds, section 4).

**Two dashes, the second stronger for every hit in between (league_akali R, Perfect Execution).** League's second
cast deals more to targets missing health; nothing reads health, so it counts her own work instead. The cast
(`Targeting` on `EnemyChampion`) clears the rungs `r_s1`..`r_s8`, adds a 180-tick `r_window` buff and dashes with
`RushTime {speed: 8000, tick: 9, penetrate: true}` (72000 toward the target, through it) whose `applied_effects` hit
every unit it passes. While `r_window` lasts, every champion hit (a champion-only twin on the attack, a champion-only
cone in Q, the twins of E) climbs one rung (`SwitchByBuff` from the top, as league_darius counts Hemorrhage). 150
ticks after the cast a hidden `TargetProjectile` goes to the first target with `RandomTarget {range: 70000,
casting_target: AllyOnlySelf, from_projectile: true}` in its effects (league_morgana's reach check): a 3-tick flag
when she is within reach of it; a projectile at a dead target spawns and is gone the next tick without hitting. Two
ticks later the second `RushTime` goes at the first target when the flag is there, otherwise at a `RandomTarget
{range: 70000, casting_target: EnemyChampion}` (a `RushTime` inside it heads for the picked unit), otherwise not at
all; its damage reads the ladder from the top (+25% a rung, +200% at eight). Crowd control at that moment cancels the
second dash, death cancels it (it clears `r_window`). Over 6 games 27 ults: the second dash went 11 times at the first
target, 7 times at another champion, 9 times nowhere (nobody within reach) and was lost twice to crowd control.

**Double range on the attack after a spell (league_akali Assassin's Mark).** League empowers her next attack once she
leaves the ring round the champion her spell hit; nothing reads positions, so a champion hit (Q's champion cone once
per cast, E's twins, the ult) adds a 240-tick caster buff with `range` 24000 (her own 24000 again) and
`move_speed_mult` 30, replaced rather than stacked (`RemoveCasterBuff` first: two `range` buffs would add up). A
`range` buff also stretches the distance the AI starts attacking from (section 3): the next attack began 65000 from a
pyromancer (48000 plus both bodies) and the attack consumes the buff (bonus magic damage, its own slash).

**Combos the slots play (league_akali E Q A, R E E R; 0.42.6).** league_leesin's way ("Combos the slots play"):
each combo is the slot it spends, no slot is held. E2's champion-only twin (its applied effects run only when E2's
target is a champion) adds `e2_on` (120 ticks), and while R's `r_window` is open it also removes the window and,
6 ticks later, runs the second dash's own effects (`CasterAnimation ult2`, the `RushTime` that reads the ladder)
toward that champion - R's scheduled second dash finds no window and stays put, and the ladder already holds E2's
rung. Q in `e2_on`, 5 ticks after the fan and with the ring armed, flings the kama: a `RandomTarget` (48000, the
empowered range) on `EnemyChampion` plays `attack_p` and lands the attack's own empowered hit 7 ticks later (the
ring spent). In 12 simulated games 44 E2s landed on champions: 17 Qs flung the kama (all hit), 6 second dashes came
off E2 (on R's tick 90 on average, not 152; all hit). In mid lane against base mages (720 games) the kill difference was +1.38 before and +1.36 with the combos (about 2% more damage dealt): the same strength.

**Every third attack cleaves, attack speed after every spell (league_diana Moonsilver Blade).** The attack walks two
240-tick caster stacks (league_masteryi's Double Strike, branched at `start_timing` 1); the third plays its own strip
(`CasterAnimation attack_p`, the hit 13 ticks after the branch instead of 10) and adds to the plain hit a
`RangeEffect` circle (radius 18000 at `Forward {offset: 18000}`, `EnemyWithoutTower`) of `ApAttack`: the target stands
in it, so it and whoever is next to it take the magic cleave. Every spell removes and re-adds a 180-tick
`attack_speed_mult` caster buff (one instance, section 5).

**A mark the caster reads (league_diana Moonlight).** League's Moonlight sits on the enemies Crescent Strike hit, and
Lunar Rush has no cooldown on a marked one. Nothing reads a buff on the target (`SwitchByBuff` checks the caster), so
the mark is a caster flag: every unit the crescent hits refreshes a 180-tick `moonlight` buff on her (and gets a
crescent picture of its own for as long, an `AddBuff` with a `view_buffs` entry); a 20-tick caster lock plays the hit
sound once when the crescent goes through a whole camp. Lunar Rush spends the flag whatever it dashes at.

**A dash that refreshes on the mark, inside one cast (league_diana Lunar Rush).** No effect resets one skill's
cooldown (`skill_cooldown_mult` caps both skills at once, so a refund would bring Crescent Strike back too and chain
Q-E-Q-E), so the refresh is the second dash itself: a `Targeting` cast on `EnemyWithoutTower` (range 45000) swaps
`moonlight` for a 90-tick `e_again` flag, dashes (`MoveToTarget`, `CasterAnimation skill2`) and, 8 ticks after the
landing (`Delayed` in the dash's `end_effects`), spends `e_again` on a second dash: `RandomTarget {EnemyChampion,
45000}` with a 1-tick `e2_aim` flag, else `RandomTarget {EnemyWithoutTower}` (the Briar/Ahri tiers), each a
`MoveToTarget` with the same hit. League's reset sound (`DianaTeleport_reset`) plays on the second one. In the
simulation (60 games, 10 minutes) she cast it 31 times a game and dashed twice on 21 of them, the second dash onto a
champion 6 times.

**Orbs that burst one by one on the enemies near her (league_diana Pale Cascade, folded into Lunar Rush).** On the
first arrival, when its own 600-tick cooldown buff is gone: a `Shield` through a `RangeEffect` on `AllyOnlySelf`, a
`WithShield` picture buff, and three orbs - caster buffs `w_orb3` -> `w_orb2` -> `w_orb1` whose `view_buffs` show 3, 2
and 1 orbs circling her (each re-added with the time left, so all end with the 5 s). `Delayed` pulses every 15 ticks
(from tick 6, while a `w_live` buff lasts) pick a random enemy within 20000 (`RandomTarget`), fire a
`TargetProjectile` orb at it (the damage and the burst in its `applied_effects`) and step the orb count; the third
removes `w_live` and shields her again (shields add up). With enemies next to her the three burst within 0.6 s; with
nobody in reach the orbs wait. Measured: 23 casts a game, 2.9 orbs a cast.

**Draw them in, then the moon crashes, harder for each champion (league_diana Moonfall).** A `Targeting` cast on
`EnemyChampion` (range 25000): a `RangeEffect` (radius 50000) on `EnemyChampion` with `Grab {speed: 2500}` (no `tick`:
each stops at her, section 4 "Pull vs Grab"), a 40% slow for 2 s and a count - league_kayle R's two-flag count taken
to three (`SwitchByBuff r_n2 ? add r_n3 : SwitchByBuff r_n1 ? add r_n2 : add r_n1`, 70-tick flags). 60 ticks later a
`Delayed` checks `r_n1` (no champion drawn: no crash) and picks one of three `RangeEffect`s by `r_n3` / `r_n2`: the
damage +35% for each champion beyond the first. The falling moon is a `CasterViewEffect` played 20 ticks before the
crash (radius 40000 round her). Keep the pull wider than the cast range: the AI casts from `range` plus both bodies
(league_garen E, league_leesin R above), so with League's proportions (range 30000, pull 32000) 20 of 42 casts came
from 45000 or more centre to centre and 37% of the ults drew nobody - the ring on the ground and no moon. Range 20000
drew 92% but the AI cast it a quarter less often (one batch +0.01 against +0.44); range 25000 with a 40000 pull drew
84% (2.7 casts a game, 1.22 champions a cast that drew) and took lane 1 from +0.44 / +0.55 to +1.04 / +1.03. The user
then wanted it wider: a 50000 pull and a 40000 crash (from 40000 / 32000, the cast range kept) drew nobody on 4% of the
ults instead of 9%, 1.21 champions a cast instead of 1.10, and put 0.86 champions under the moon instead of 0.74 (the
same 1440 games): +1.25 / +1.16, paired +0.17 (standard error 0.11). The crash catches fewer than the pull because two
in five drawn champions die before the moon lands; nine in ten of the living ones stand inside it (its radius plus
about 20000 centre to centre). The grab is crowd control for league_yasuo's R (section 7
"Blink to a crowd-controlled champion"): beside her he cast it 1.23 times a game (1.19 after the widening).

**Attack speed that stacks and falls off one stack at a time (league_jax Relentless Assault).** League gives a stack
per attack for 2.5 s, eight at most, and loses them one by one once he stops. Every attack runs a `SwitchByBuff`
chain from `ra_8` down: the highest stack present is the count (the lower ones always outlast it), then all are
removed and `ra_1`..`ra_n` added again, one more than before and at most eight, each an `attack_speed_mult` 7
caster buff whose duration grows toward the bottom - the top one 150 ticks, every lower one 15 more - so
after his last attack they end one at a time a quarter second apart. Separate names keep the count readable
(same-name buffs add up too, section 5, but `SwitchByBuff` cannot count them).

**An ability folded in on its own cooldown, spent by whichever comes first (league_jax Empower, W in Q).** W's
cooldown is a caster buff (`w_cd`, 300 ticks); W is ready while it is absent. The basic attack picks its animation
on tick 1 (`start_timing: 1`, the hit in a `Delayed` of 9 ticks, league_riven's way): with W ready it adds `w_cd` and a
flag that lasts until the hit (`w_hit`) and plays League's Crit smash (`attack_w`), and the hit spends the flag on the
bonus `ApAttack`; else `attack_r` while the ult's buff lasts, `attack_e` in Counter Strike's stance, or the plain
swing. Q's landing (`MoveToTarget`'s `end_effects`) checks `w_cd` as well and spends W the same way, so Empower rides
the leap when it is ready (League's W then Q) and otherwise the next attack.

**A leap that opens waves and camps too, on the AI's own target (league_jax Q, Leap Strike).** A `Targeting` cast on
`EnemyWithoutTower` (range 50000) with `MoveToTarget` onto the cast target. league_briar's aim - a `RandomTarget
EnemyChampion` in reach first, the cast target only when none is found - made Jax worse by more than a kill a game
(the same kit: -1.25 against -0.09 on the same seeds): the random champion was often the back line, and he leapt into
the whole team. The AI already picks champions for a `Targeting` skill when they are in reach (about 13 of 41 leaps
a game), so the plain cast target is kept; champion-only casts (+0.45) would never touch waves or camps.

**Dodge basic attacks while he keeps fighting, then stun round him (league_jax E, Counter Strike).** A short `None`
cast on `EnemyWithoutTower` (range 25000, 22 ticks of `CasterAnimation skill2`: the lamppost spun over his head) adds
a caster buff for the stance (90 ticks + 2) with `base_attack_damaged_reduce: 100` and `skill_damaged_reduce:
25`: basic attacks on him dealt 0 while it lasted *(SDK simulation, 2026-09-30)*, and he walks and attacks as
usual (his attacks pick `attack_e`, League's Spell3 attacks). A `Delayed {tick: 90}` checks the buff (death
clears it) and fires the counter: `CasterAnimation skill2_burst`, 4 ticks later a circle (32000) of `ApAttack` and
a 60-tick `Stun` on `EnemyWithoutTower`, and a 4% max-health `FixedAttack` on `EnemyChampion` only (the
epic monster would melt, section 2). League's +20% damage per dodged attack cannot be counted - no effect fires when
he is hit - so the damage is fixed; the recast that ends the stance early is dropped (the AI cannot press it), and the
stance is 1.5 s instead of 2 so the stun comes before the fight has moved on.

**Armour for every champion the slam hits (league_jax R, Grandmaster-at-Arms).** A `None` cast on `EnemyChampion`
(range 30000). On the slam frame a circle (35000) of `ApAttack` on `EnemyWithoutTower`, and a second circle on
`EnemyChampion` whose effects are `SwitchByBuff r_on` -> `AddCasterBuff r_extra` (15 armour and magic
resistance), else `AddCasterBuff r_on` (40 each, 480 ticks): a `RangeEffect` runs its effects once per unit,
so the first champion gives the base buff and every other one an extra instance (same-name buffs add up, section 5).
While `r_on` lasts R's passive procs on every second attack instead of every third and the attacks play League's
reversed-grip thrust (`attack_r`).

**Every third attack, every second one while a buff lasts (league_jax R's passive).** Two caster counters of
150 ticks (`gm_1`, `gm_2`), refreshed by every attack: without `r_on`, `gm_2` -> the proc (the bonus
`ApAttack`, both counters removed), `gm_1` -> swapped for `gm_2`, neither -> `gm_1`; with `r_on`, either counter -> the
proc. The counters' duration is League's 2.5 s window. It works from level 1 (nothing reads level 5).

**Ability power that stays until he dies (league_veigar Phenomenal Evil Power).** No native passive of game 0.6 stacks
ability power (`ghost` adds attack and attack speed, `dancer` only counts kills), so every stack is one more instance of
a `Permanent` caster buff with `magic_power: 1` - instances add up (section 5) and nothing needs to count them. A spell
hit on an enemy champion adds one: Q through a champion-only `TargetProjectile` fired a tick after each of its first two
hits (league_akali's twin), the cage through a second `ApplyInProjectile` on `EnemyChampion`, W through a champion twin
of its `RangeProjectile`, R on its own hit. A unit Q kills adds one (the kill trigger on each of Q's first two hits,
a flag each), a champion he kills five (the kill trigger on champion-only twins of the attack, Q and W, and on R's
bolt). Death clears them all (section 5): in one simulated game he had 92 by 7.8 minutes and none after he died at 7.9.

**A bolt through the first two (league_veigar Q, Baleful Strike).** A `Direction` cast on `EnemyWithoutTower` fires a
penetrating `LinearProjectile`; its applied effects walk two caster flags from the top - with `q_n2` nothing, with
`q_n1` the second hit (the damage, then `q_n2`), else the first (the damage, then `q_n1`). The flags last 20 ticks (the
flight takes 14) and the cast clears them first. In 72 casts of one game 39 hit two units, 25 one, 8 none, none three.

**A cage that stuns whoever touches it, Dark Matter on its centre (league_veigar E with W folded in).** A `Targeting`
cast on `EnemyChampion`; 24 ticks after the release a hidden `ParabolicProjectile` (`travel_time` 1, league_annie R)
lands on the champion's spot and its `end_effects` start everything there: the cage's picture and W's two (the target
ellipse, shockwave and scorch at `z` -1 under the units, the sphere and its burst over them) as `ViewEffect`s on the
point (away from the caster, so they show - league_thresh R); two `ApplyInProjectile` (tick
180, circle 34000) - one on `EnemyWithoutTower` with `Stun` 60, which reaches every unit once, one walking in
later on the tick it touches the edge (section 4), and a twin on `EnemyChampion` for the stack and R's ladder; and W as
two `RangeProjectile`s (circle 22000, `delay` = `apply` = 45) on the same centre: the damage on
`EnemyWithoutTower`, its champion twin the stack, the ladder and the kill trigger. League stuns only a unit that
crosses the cage's edge; a zone is a disc, so whoever stands inside when it forms is stunned at once. W lands
0.75 s after the cage forms, inside the stun. In one game of the first draft 17 casts stunned 26 champions and 22
minions (the stun was 1.5 s then; 1 s since the balance pass). The cage forms on its target, who is always caught, so
widening it only adds the others: 28000 -> 34000 (players asked for a wider E) took the champions stunned per cast
from 1.54 to 1.63 and the casts catching two or more from 33% to 39%; 36000 caught 1.64 (SDK simulation, mid against
the five base mages, 120 games each, 2026-10-01).

**R stronger for every spell hit in a row (league_veigar R, Primordial Burst).** League adds up to 100% against the
target's missing health; nothing reads health (section 3), so it counts his own work like league_akali R2: every spell
hit on a champion walks the rungs `r_s1`..`r_s4` from the top and re-adds all of them with a fresh 240 ticks (remove,
then add), so the ladder lasts 4 s after the last hit rather than the first and never has a gap. R's bolt reads it from
the top when it hits (+25% a rung) and clears it. The action starts on tick 2 - a caster view gathers the orb at the
staff he raises as he leaps - and fires the bolt from a `Delayed` 10 ticks later (league_akali E's shuriken), so the
orb flashes as the bolt leaves at the top of the leap; the bolt's `y_offset` -15000 lifts its picture 20 px over the
pivot (5000 - `y_offset`, see "A beam from a raised weapon"), level with his shoulders rather than his waist.

**Two quick attacks after every spell, each taking a second off the cooldowns (league_taric Bravado).** Every spell (E,
the Q/W cast, R's start) adds two 240-tick caster buffs `brav_1` and `brav_2` and a 240-tick `attack_speed_mult` 100.
The attack branches at tick 1 (league_jinx's way): `brav_2` first, then `brav_1` together with the speed buff, each
playing `CasterAnimation attack_p` with the hit in a `Delayed` 9 - bonus magic (`ApAttack` 30 + 20% AP + 3% of his
maximum health, the stand-in for League's armour ratio), a Starlight's Touch stack and the cooldown cut. League takes
1 s off his basic cooldowns per empowered hit; nothing subtracts time, and `skill_cooldown_mult` only caps each
remaining cooldown at cooltime x 100 / (100 + mult) (section 5), while the first empowered attack lands 70-120 ticks
after the spell: with +20 per hit one cut happened in a whole simulated game. The two hits therefore add growing
values in 2-tick buffs, 55 for the first and 145 for the second, which take about 1 s each off the spell just cast
(E, cooltime 420: 337 -> 270 at the first hit, 228 -> 171 at the second, in the simulation's cooldown events) and cut
the other basic spell only when it was cast within the last 2-3 s. The same buff carries `ult_cooldown_mult` of the
opposite sign: the ult's cap uses the sum, and no ult cut showed in the events. With the cut working the kit went from
+0.97 to +1.68 kills in the same batch.

**Stacks that fill over time, counted at his actions (league_taric Starlight's Touch).** Up to three `Permanent` stack
buffs `q_s1`..`q_s3` (death clears them). Nothing runs on its own every few seconds without an icon (an `AddCasted`
on himself would show a status icon all game), so the stack timer is read when he acts: three caster timers of 300,
600 and 900 ticks; an action that finds the first gone adds a stack, the second gone another, the third gone a third,
and sets all three again - a 12 s walk gives two stacks at his first action. Bravado hits add one each. Cast as `None`
on `EnemyChampion` within 45000 the AI used it 6 times a game (nothing to score: it heals); on `EnemyWithoutTower`
within 30000 (anything he is fighting) 18-21 times. It heals him and the allied champions in a 30000 circle for 40 +
12% AP per stack spent, and removes the stacks.

**A link that repeats his spells round an ally (league_taric Bastion, folded into Q).** On its own 12 s timer the Q cast
also picks a random allied champion within 60000 (`RandomTarget AllyNotSelf`, league_janna E), shields it (80 + 40% AP
for 150 ticks), gives it 15 armour and hangs an `AddCasted` (`Heal`, period 1, 720 ticks) on it. Each run of the casted
checks Taric's 2-tick cast flags - a `SwitchByBuff` inside it reads the caster, Taric - and removes the flag it uses, so
a cast fires once there. Its effects run on the ally, so a hidden one-tick `ParabolicProjectile` lands on the ally's
spot (league_annie R) and its `end_effects` go on only when Taric stands within 110000 of it and not within 30000 of it
(two `RandomTarget AllyOnlySelf from_projectile` flags: League's link breaks at 1300 units, and an ally on top of him is
already inside his own circles); there they start Q's heal circle (a flag per stack count), E's stun (a circle bursting
on the beam's tick: a line started at a point points from the caster, section 6) or R's invulnerability circle. In the
simulation 31.7 champion heals a game came from his own Q and 8.4 from the link, and the link's E burst about 1.6
times a game. The casted shows a `heal` status icon on the ally while the link lasts.

**A beam that bursts after a delay (league_taric E, Dazzle).** A `Targeting` cast on `EnemyWithoutTower` with league_morgana
Q's aim (a random enemy champion in reach first, else the cast target): a `LineRangeProjectile` 80000 long whose hit is
the damage and a 75-tick stun. Champions here walk out of a line in a second: with League's 1 s delay (`apply` 60) and
width 12000, 24% of the casts aimed at a champion stunned one; `apply` 45 with width 18000 stunned in 65% (30 / 18000:
96%). The beam's picture carries the 45-tick charge and the burst (`delay` 57). Make the line as long as the AI casts
it *(SDK simulation, 2026-10-01, after the user saw it miss every time in lane: "对线一次都晕不到")*: the line was 62000
long at first, the AI casts at the 60000 `range` plus both bodies (median 73000, past the line's end), and the aimed
champion, which had stood still for the 0.75 s before, backs off about 23000 while the beam charges, out past the end;
almost none step aside. Checked cast by cast on the aimed champion, 29% were stunned in the first three minutes (34% over
a game, 30% in the mid lane). 80000, about as far as the AI casts it, stunned 63% (59% over a game); 72000 48%, width
30000 58%, `apply` 30 59%. The athletes' `skill_avoid` changed nothing (0 and 100 played the same games).

**Team invulnerability 2.5 s after the call, started at the fight (league_taric R, Cosmic Radiance).** league_riven R's
arming (the slot is a 3-tick `None` action on `EnemyChampion` that adds `r_armed` for 600 ticks; left unused, a 3-tick
`ult_cooldown_mult` 4900 refunds it) with league_kayle R's counting: while armed, every action and a `Delayed` pulse every
30 ticks count the enemy champions within 45000 (the `n1` / `n2` flags) and look for an allied champion in crowd
control there; two enemies, or a held ally, start it: `CasterAnimation ult`, the call's picture, and 150 ticks later a
`RangeEffect` on `AllyChampion` (radius 40000) adds a 150-tick buff with `damaged_reduce` 100 - every hit deals 1. Two
such buffs (his circle and the link's overlapping) still take 1 a hit (measured). About 1.25 starts a game, 2.1
champions made invulnerable each; a dead Taric's pending `Delayed` never lands.

**Attack range at levels 3, 6, 9 and 12 (league_tristana Draw a Bead).** League adds range every level; nothing reads a
level but `SwitchByLevel3`, so the stages are league_kayle's health probe (above, "Stages at levels 5, 8 and 12"): at level
3 `SwitchByLevel3` alone adds the first `Permanent` caster buff (`range` +2500); for 6, 9 and 12 a 3-tick `Shield` of S on
herself (S between 20% of her maximum health one level below and at the stage: 261, 315 and 369 for 900 + 90 a level), a
`WithShield` flag and a `FixedAttack` on herself - the flag gone 2 ticks later means the hit broke the shield, so the
level is there. Three things broke Kayle's probe on a marksman: (1) in the attack (`attack_type` `BaseAttack`) the
probe's `FixedAttack` rolls her crit chance, and a crit (2x) broke the shield at any level - stage 12 at level 4 with
25% crit from items - so the probes run only in her skill slots (E, and W's slot every 10 s), and the attack adds only
the level-3 stage, which needs no probe; (2) an enemy hit landing in the probe's 2 ticks broke the shield too, so the
probe runs under a 3-tick `damaged_reduce: 99` caster buff and its own hit is 100 times as big (`hp_ratio: 2000`, 20% of
her maximum health after the reduction); (3) a hit the reduction does not cover (a tower's) can still break it, so in
a fight a stage needs two passes in a row - the second within 60 s of the first (a 3600-tick `pass6`/`pass9`/`pass12`
flag; E alone came every 40 s in some games) - while her first action of each life, away from the fight, re-reads
every stage (death cleared them) in one pass and sets the 5 s `probe_cd` itself. Kayle's 99-against-100 check against
damage amplification is left out: in a fight enemy hits broke it so often that a stage came minutes late. Every stage
buff is added behind its own `SwitchByBuff` guard (two probes in one tick would have stacked it twice). Items with
health move a stage earlier (her attack-damage and attack-speed items have none). In four simulated 10-minute games no
stage came early: the level-3 stage within a second of the level, 6 10-36 s after it, 9 18-43 s, 12 18 s (the one game
that reached it).

**A charge that sticks, counts her hits and blows on the fourth (league_tristana E, Explosive Charge; Q Rapid Fire
folded in).** The cast gives Rapid Fire's attack speed (a caster buff, one instance) and throws the charge, a
`TargetProjectile` whose hit adds two `AddCasted {casted_type: Fire}` to the carrier: one polls every 2 ticks for 250
ticks, one replays the bomb's picture every 10 ticks. The count lives on the caster (`e_1`..`e_3`, `e_live`, a 240-tick
`e_timer`); her hits climb it - the attack's cannonball, W's landing and R's blast (the areas once per cast, behind a
3-tick lock) - and nothing tells which unit a hit is on (league_vayne's Silver Bolts), so any of her hits counts. The
fourth sets a 4-tick `e_boom` flag; the poll finds it within 2 ticks and detonates the charge on its carrier, wherever
the fourth hit landed; without it, a poll that finds `e_live` but no `e_timer` (4 s gone) detonates it with the stacks
held. A detonation is a one-tick hidden `ParabolicProjectile` from the casted effect (projectiles from an `AddCasted`
fly from the caster to its target, league_annie's Tibbers) whose `end_effects` start the damage circle, +25% a stack,
and a champion twin for the kill check; at full stacks W resets when the carrier is a champion (`e_champ`, a caster flag
the charge's champion-only twin sets as it plants; a 1000-radius `EnemyChampion` circle round the blast caught a
champion beside a minion carrying it). The picture casted chooses the view by the stack flags (the bomb with 0-3 red
lights), so it follows the count, and the carrier's death clears both casted effects: no bomb floats over a body, and a
carrier killed before 4 s drops its charge. A `Fire` casted shows a burn icon on the carrier while it lasts - fitting
for a bomb - and damage from inside it counts as `Dot`. Rapid Fire's steam is not a buff view (a buff's picture stays on
a body, league_garen's spin, and may not turn with her) but a 1 s `CasterViewEffect` with `is_follow`, played every
second while the buff lasts (`Delayed` pulses behind a `SwitchByBuff` on it).

**Units her basic attack kills explode (league_tristana, Explosive Charge's passive).** A projectile in another projectile's
`applied_effects` never spawns, and a `Delayed` queued on a unit that died runs only its pictures, so the explosion cannot
start from the killing hit. The attack fires, beside its cannonball, a hidden `ParabolicProjectile` that lands 10 ticks
later where the target stood when she fired; its `end_effects` wait 8 ticks and read league_jinx's kill check, run here on
every unit: the cannonball's hit adds a 24-tick caster flag `kx` and a 3-tick `AddCasted` on the target that removes it
while the target lives. A flag still there means the unit died, and the explosion circle starts on the landing point. The
flag has to outlast the check from the latest hit (the cannonball flies up to 12 ticks).

**A jump her shots set off, its cooldown reset by her takedowns (league_tristana W, Rocket Jump).**
`skill_cooldown_mult` caps every skill's cooldown at once (the ult's too, section 5), so a W reset through it would
re-arm E+Q as well - a full-stack detonation would hand her the next charge at once. W keeps its cooldown as an 18 s
caster buff `w_cd` instead, which her champion kills (the kill check on every damaging hit) and full-stack detonations
on champions remove. Each source keeps its own kill-check flag (`kc_a`, `kc_e`, `kc_w`, `kc_r` for the attack, E, W and
R): with one flag for all, a check whose target lived could read the flag another source had set a tick before that
one's own removal ran - a W landing's check and the detonation its stack set off land three ticks apart. A slot of its
own could not time the jump: cast every 1.5 s (a 3-tick action on the `idle` tag, league_kayle R's arming action) it
jumped when it should but cost her about 0.7 kills a game in the simulation - her attacks waited for it - and cast every
10 s it met the charge at two or three stacks once in ten minutes. So her shots set it off: the attack's champion-only
twin (the kill check's) waits a tick after its hit - the cannonball's own hit has counted the stack by then - and,
without `w_cd`, with the charge on a champion (`e_champ`) holding two or three stacks, jumps her onto the champion it
hit: a `MoveToTarget` in a projectile's `applied_effects` moves the caster to the unit hit, and a `CasterAnimation`
there plays on her (both in the simulation log). The landing adds the stack the next shot turns into the fourth. When
she fires, the attack counts the enemy champions within 25000 (two 3-tick flags, league_kayle R's count) and with one of
them jumps her away from it (`MoveBack` 3500 x 11; two, League's "surrounded", never came up). The slot stays, cast
every 10 s on a champion within 80000, for the same escape and Draw a Bead's probes. A `CasterAnimation` holds the
caster from acting while it plays (league_garen's 3 s spin), so the 32-tick jump strip is not cut by her next attack: 7
ticks' crouch, the move from a `Delayed`, and the landing's damage, slow and stack where she comes down. In four
simulated games she jumped 5-11 times a game - 19 times onto a champion, 10 away, often just after a full-stack
detonation reset W (jump in, blow the charge, jump out) - and W was reset 18 times; the slot alone had jumped 0-1 times
a game.

**A cannonball that knocks back the target and those round it, stunned where they land (league_tristana R, Buster Shot).**
A `Targeting` cast on `EnemyChampion` (60000), the nearest champion within 30000 first (league_lucian R's ring). The
cannonball's hit only plays its pictures and, from a `Delayed {tick: 1}`, a one-tick hidden `ParabolicProjectile` whose
`end_effects` start the blast: a circle on `EnemyWithoutTower` whose applied effects deal the damage, `Knockback {speed:
3000, tick: 10}` (away from her, as league_vayne's Condemn measured) and, `Delayed` as long as the knockback, the stun where
each unit lands - the target is in its own circle, so it is hit once, like the rest. The knockback and the stun count as
crowd control for league_yasuo's R: with her at bottom in his team he cast it on champions 1.12 times a game
(league_vayne 1.92, the base archer 0.65 in the same batch; league_ahri 1.27, league_ekko 1.12 before) - no change.

**Projectiles that leave the muzzle, not her belly (league_tristana).** A `TargetProjectile` starts at the caster's
pivot; its `y_offset` lifts the picture (`5000 - y_offset` over the pivot), so each picture is lifted to about its
firing frame's bell (the attack 3 px over the pivot: 2000; E, the barrel lowered, 4 px under it: 9000; R 1 px under
it: 6000), and its view (`repeat: false`) starts with an empty frame for the ticks the ball needs from her pivot to
the bell (3, 5 and 3 at 6000, 4500 and 7000 a tick), then loops, and holds a frame long enough to outlast any flight.
The flashes at the bell are `CasterViewEffect`s played in the same tick, with `is_follow`: played without it, they
stayed on the side they were played on and showed behind her once she turned ("小炮转身了那个火就在小炮的身后",
2026-10-01). Following her is not following her sprite: the view stays where it was put on her while the bell moves in
the frames after the shot (R's flame burned on in front of her for ~300 ms after the recoil had thrown the cannon over
her head: "枪口的火还是没跟着枪的方向 固定住了"). So the fire is timed to the frames whose bell stays put - the
attack's shot frame and the next hold the bell still, R's flame burns out in its 90 ms shot frame - and a view's tag
can be built from parts at different spots (E's fire moves a square back with its 4th frame); the smoke after the
fire may stay where it was blown out. Attack speed shortens the attack's frames but not a view's, so keep that fire
within the frames at base speed. `y_offset` is not only the
picture (league_lucian's double shot moved by a tick): when she was cut to 34 rows, 5000 / 13000 / 9000 (the new
bells' middles) made the flights 1-2 ticks longer on average (the bolt 8.4 -> 9.4 ticks, the charge 13.1 -> 15.3 in
one simulated game) and her kill difference fell from +2.06 to +1.33 on the same 24 seeds, so the tested values stay
and the pictures fly 3-4 px over the bells' middles, still inside them. The cost is not general: league_caitlyn's
projectiles went from `y_offset` 3000 to their muzzles (-11500 for a rifle 16.5 px over the pivot, -7000 / -6500 /
-2500 / -4000 for the Headshot, the net, Q and R; `tools/art/import_caitlyn.py` checks the kit against the measured
muzzles and starts each view empty for ceil(muzzle x / speed) ticks) and her mean stayed +2.30 on the same 288 games.
A high muzzle has another cost: the bullet flies at the target's pivot, so from 16.5 px up it fell 12 degrees over her
70-85 px reach and its turned picture looked crooked (the user: "平A出去的子弹看起来是歪的"). League's Caitlyn fires
from the hip; her attack and Headshot now fire on Codex's lowered-barrel frames (import_native `ORDER` holds them two
slots and drops the frame that threw the barrel up; muzzles 6.5 and 8 px up, `y_offset` -1500 / -3000, about 5
degrees). Keep a shot frame's muzzle within about 8 px of the pivot's height, or the shot tilts.

**A weak spot on the target without state on the target (league_fiora Duelist's Dance).** League shows a Vital on one
of four sides of a champion and strikes it with a hit from that side; nothing reads a direction or keeps state on
another unit, so her own caster flags decide. `v_cd` (180 ticks) starts when a Vital is struck; while neither `v_cd`
nor `v_on` is on her, her next hit on an enemy champion reveals one (`v_on`, 180 ticks, the chime); while `v_on`
lasts, her next champion hit strikes it: a `FixedAttack` of 20 + 10% attack + 4% of the target's max health
(`target_hp_ratio`), a `Heal` on her and two move-speed buffs (+30% for 90 ticks, +30% for 45: +60% that fades in
two steps). Every hit reaches the hook through a champion-only twin `TargetProjectile` (see "Kill trigger"); the
attack's and Q's damage ride a carrier of the same speed, so the twin lands the same tick. The mark is a
`ViewEffect` on the champion every 20 ticks while `v_on` lasts, each piece behind an alive gate: a `Delayed` on a dead
unit still plays its pictures but skips `AddCasterBuff`, so a 2-tick caster flag added the tick before each piece
says the unit lived (league_annie's Tibbers).

**A dash-stab that arms the next two attacks (league_fiora Q with E folded in).** A `Targeting` cast on
`EnemyWithoutTower` (42000): a `RandomTarget EnemyChampion` in reach first (it sets `q_aim`), else the cast target,
gets `MoveToTarget` (4000 a tick) whose `end_effects` stab: a carrier of the damage, the champion twin, and E. E's
cooldown is its own caster buff (`e_cd`, 480 ticks); when it is absent the stab adds `e_1` and `e_as` (+50% attack
speed, 240 ticks). The attack picks on tick 1: `e_2` -> the critical thrust (`CasterAnimation attack_e`, `Attack`
at 160% attack, `e_2` and `e_as` removed), `e_1` -> the slowed first hit (30% for 60 ticks; `e_1` becomes `e_2`),
else the plain thrust.

**Parry, then a stab that stuns only if the parry blocked a hit (league_fiora W, Riposte).** A `Targeting` cast on
`EnemyWithoutTower` (45000, 64 ticks). A caster buff `w_parry` (45 ticks) with `damaged_reduce` 100 and `cc_immune`
(hits then deal 1); a 1-point `Shield` on herself (a self-only `RangeEffect`, 60 ticks) and `AddCasterBuff w_guard`
of duration `WithShield`: the first hit breaks the shield and `w_guard` goes 2 ticks later (section 5). The stab is
queued on her own unit (a self-only `Delayed` of 47 ticks), so it comes even when the cast target died during the
parry: a `RandomTarget EnemyChampion` within 55000, else an `EnemyWithoutTower` one, gets a `LineRangeProjectile`
(55000 x 16000, `delay` 12, `apply` 2: the hit on tick 1, gone on tick 11, which is how long its picture lasts) and
a champion-only, non-penetrating `LinearProjectile` (20000 a tick, radius 8000) for the first champion: `w_guard`
still on -> a 50% slow for 90 ticks, gone (she blocked something) -> a 60-tick `Stun`. League stuns when the parry
blocked crowd control; nothing tells a blocked stun from a blocked hit, so any blocked damage counts.

**A challenge whose pace follows the fight (league_fiora R, Grand Challenge).** The AI casts an ult slot on
`EnemyChampion` while it walks in (65000-235000 away here), so the slot is a 3-tick `idle` action with `casting_type:
None` that only arms it for 600 ticks (`r_armed`, league_riven's R): a `RandomTarget EnemyChampion` within 35000 starts
it at once, else the champion twin of her next attack does; left unused, a 3-tick `ult_cooldown_mult` 4900 refunds
it. The start (effects on the champion): `CasterAnimation ult` (18 ticks, the salute), the passive's Vital removed,
`r_on` and four rung flags `r_v4`..`r_v1` (480 ticks), +20% move speed, and Bladework armed (`e_1`, `e_as`; E's own
cooldown untouched). While `r_on` lasts the hook takes the top rung instead of the passive: the passive's strike with
the gold picture and a 3-tick `skill_cooldown_mult` 100 (removed first, so two never stack), which caps Q's and W's
remaining cooldowns at half - League's Lunge refund, spread to both since no field speeds one skill alone. The user
asked for the pace to follow the fight ("破阵速度 你要时快时慢啊", "根据战场情况"): on the target, the two quick attacks
and a Lunge strike three Vitals in about 1.3 s; when the target gets away or she is held, only the halved cooldowns
bring her back. The remaining Vitals show as `r_m4`..`r_m1` (a `SwitchByBuff` ladder on the rungs) in 20-tick pieces
behind the alive gate, from tick 22: the challenge's own picture covers the first piece, its four crests landing
where the loop's stand.

**A healing zone where the duel was won, also when someone else took the kill (league_fiora R's Victory Zone).** The
fourth Vital sets a 4-tick caster flag `r_won`; an `AddCasted` poll (period 2, `Bleed`) put on the challenged champion
where R starts finds it, removes it and lobs a `ParabolicProjectile` (`travel_time` 1; a projectile from an `AddCasted`
flies from the caster to its carrier) whose `end_effects` place a `RangePeriodProjectile` (tick 180, period 30, circle
35000, `Heal` on `AllyChampion`) and its picture as a `ViewEffect`. The Vitals are rung flags on her, so any champion
she hits during R takes one (16 of 42 R strikes in 6 simulated games): until 0.71.0 the fourth one lobbed the zone onto
whoever took it, and players saw it under another hero's feet (tools/fix/fix_fiora_r_zone.py). A target that dies after at least one Vital (`r_struck`), by anyone's hand, is found from her side: the
target's picture pieces add the 2-tick `r_alive` caster flag the tick before each piece, so a self-only `Delayed` every
60 ticks (a multiple of the pieces' 20) that finds it missing while `r_on` lasts means the target died, and the zone
lands on her own spot (its picture a `CasterViewEffect`: a `ViewEffect` on her own spot never showed, league_thresh
R). Checks every 20 ticks made the file 972 KB (every hook carries the whole ladder); every 60 keeps it near 580 KB.

**A hop held until the first hit, untargetable in the air (league_fizz E, Playful / Trickster).** The user wanted the
E "灵活根据战场判断 有时候E可以躲技能 有时候可以直接砸" (sometimes dodging spells, sometimes a straight slam). Nothing tells
that a spell is on its way, so the first hit on him is the signal. A `Targeting` cast on `EnemyWithoutTower` (range
45000, a 3-tick action on the `idle` tag) hops at once when no enemy champion is within 50000 (waves, camps); with one
near it holds the hop for up to 60 ticks: a 1-point `Shield` on himself (a self-only `RangeEffect`) and a `WithShield`
guard flag - the first hit breaks the shield, the flag goes 2 ticks later (section 5) and the next pulse, 3 ticks
apart, hops; nobody hits him, the hop comes at the end of the wait. The pulses ride one invisible `RangePeriodProjectile`
(radius 150000, `period` 3, `applied_target: AllyChampion`) started from Ekko's anchor on his spot, each application
asking `RandomTarget {AllyOnlySelf, from_projectile: true}` whether he is in it: the hop is written once instead of
once per pulse (a `Delayed` per pulse made the kit 980 KB, the zone 100 KB); the first pulse that hops removes the
armed flag, so a pulse per allied champion in the zone still hops once. The hop is self-only: `CasterAnimation skill2`
(50 ticks), `CasterInvisible` and a `damaged_reduce` 100 / `cc_immune` caster buff for 38 ticks (League's
untargetable; a self-`Banish` would blind his team, section 4), on tick 6 a `MoveToTarget` at 3000 a tick onto the
nearest enemy (rings of `RandomTarget`: a champion within 20000, then 45000, then any unit) - the vault -, on tick 38 a
second dash at 8000 onto the nearest again and on tick 42 (the strip's landing frame) the slam round him: damage and a
2 s slow. A crowd-controlled Fizz does not hop (league_missfortune R's `AllyChampionInCC` within 1). In a simulated game
about 26 hops, a third of them held, each 2-4 ticks after the hit that set it off; enemies mostly lose him while he is
invisible, so few hits land on the hop itself.

**Playful at once after Q or with the fish on (league_fizz Q E, R E; 0.42.9).** E's enemy check (the `RandomTarget` that starts the 1 s hold) is skipped while `q_on` (a champion-only twin on Urchin Strike's hit, 60 ticks) or the kit's own `r_stuck` (the fish on a champion, 140 ticks) holds, so E jumps at once onto the nearest champion; the jump is still written once. In 6 games 6 Es came after a Q through a champion and 14 with the fish on, 19 of them jumped at once. In mid lane against base mages (720 games) the combos gave +2.06, against the +1.75 recorded for the old kit on the same seeds - within the noise.

**A fish that sticks, the shark sized by its flight (league_fizz R, Chum the Waters).** A `Direction` cast on
`EnemyChampion` (range 85000) throws a non-penetrating `LinearProjectile` on `EnemyChampion` (speed 6000, radius 10000:
it passes minions). Two caster windows set at the throw (`r_t1` 3 ticks, `r_t2` 5) tell its flight time when it hits:
within the first the small shark, within the second the medium one, after them the big one (League's three sizes by
distance). The champion gets the fish's slow (40 / 60 / 80%) as a buff whose `view_buffs` picture is the fish, a second
buff whose picture is the ring of shark teeth under him (`z` -1), and a `Delayed {tick: 120}` one-tick lob
(`ParabolicProjectile`, league_annie R) onto his spot, whose `end_effects` play the shark and a `RangeProjectile`
(radius 24000 / 30000 / 36000, `apply` 1) of damage, `Airborne` 60 and the slow - the shark follows the champion for
the 2 s. A miss: the fish's `end_effects` (run where it stopped, on a hit as well) wait a tick and look for an
`r_stuck` caster flag the hit sets; without it the fish lies there and the big shark bursts on that point 119 ticks
later (a `Delayed` in `end_effects` keeps the point). At speed 3500 half the fish missed - the AI throws when the
champion is 0-8 ticks of flight away and targets walked out of the line - at 6000 one in 22. The tiers are set on the
flight the AI actually gives (about 22% small, 44% medium, 34% big), not on League's distances.

**An empowered attack whose kill cuts its cooldown (league_fizz W, Seastone Trident, folded into Q).** W's cooldown is a
caster buff `w_cd` (360 ticks); while it is absent the attack picks the strike at tick 1 (`CasterAnimation attack_w`,
the hit on tick 16, the strip's stab) and Q's hit takes it too (League's W then Q). The strike's damage rides a
carrier `TargetProjectile` with league_jinx's kill check on any unit (a minion it last-hits counts, as in League): the
flag still there 4 ticks later swaps `w_cd` for a 60-tick one - in a simulated game 17 of 46 strikes killed, mostly
minions. W's passive bleed is an `AddCasted Bleed` on every attack and Q hit (each its own instance), carried by a twin
on `EnemyWithoutTower` so towers take none. The passive, Nimble Fighter, is a `Permanent` caster buff with
`base_attack_damaged_reduce` 12 added by any action that finds it missing (death clears it); "ignores unit collision"
has no field - BuffState's only movement flag is `ignore_wall` - and is left out.

**A blink behind the target and a forced critical strike (league_shaco Q, Deceive).** A `Targeting` cast on
`EnemyWithoutTower` (45000, so camps get it too): a puff where he stood (a `CasterViewEffect` that does not follow),
`CasterInvisible` (90 ticks), `RushMoveToBack` (15000 a tick: he lands 15000 past the target) and a caster flag
`q_ready` (150 ticks). The attack picks on tick 1 (`start_timing` 1, its hits `Delayed`): with `q_ready` it removes it,
plays `attack_q` and on the hit tick adds a 2-tick caster buff with `crit_chance` 100 just before an `Attack` of
20 + 85% attack. The roll happens when the `Attack` lands (section 4: chance = the stat plus buffs), so the backstab
always crits (2x) and the buff is gone before the next hit; in a logged game every backstab came out critical.

**Backstab without facing (league_shaco's passive).** Nothing reads where a unit faces, so "from behind" is built
from what shows a back: Q's landing hit always, and hits on champions in crowd control - a feared champion runs
away. Next to the attack's damage (and the shiv) an invisible twin `TargetProjectile` (100000 a tick, it lands the
next tick) with `applied_target: EnemyChampionInCC` adds 15 + 25% attack and its own picture (in a `BaseAttack`
action it can crit); the clone's strikes count the backstab in their ratio.

**Two fears from one box: champions shorter than the rest (league_shaco W, Jack In The Box).** A `Position` cast on
`EnemyWithoutTower`: a hidden `ParabolicProjectile` (`travel_time` 12) lands the box on the spot and its
`end_effects` show it landing; `w_arm` ticks later it pops. A `RangeProjectile` on `EnemyChampion` gives `Fear` (60
ticks) and a 2-tick `cc_immune` buff, and a `Delayed` of 1 tick a second one on `EnemyWithoutTower` gives `Fear` (90
ticks): the champions, immune for that tick, keep the shorter fear, minions and monsters get the longer one (League's
split). Then a `RangePeriodProjectile` (300 ticks, period 30) shoots everything round it. The box is not hidden and
does not wait for someone to walk by: the AI would cast a trap anywhere, so it goes off at the enemy's feet.

**A clone that rides the target and blows up where it died (league_shaco R, Hallucinate).** A `Targeting` cast on
`EnemyChampion`: he vanishes (60 ticks) and 12 ticks later an `AddCasted` (`Bleed`, period 4) on the champion carries
the clone (league_annie's Tibbers). Every run plays the clone's idle frame on the target, or strikes (10 + 40%
attack, the backstab included, and its attack frames) when Shaco's own hits set `r_hit` (each of his hits adds the
6-tick flag while `r_live` lasts) or after 60 ticks without one; a 24-tick `r_pic` flag lets the strike's picture
play out before the idle frame comes back. After 300 ticks it explodes where the champion stands: 150 + 100%
ability power round it and three mini boxes (the W pop with 45 / 75-tick fears and 150 ticks of shots). When the
champion dies first it explodes where he fell: every run refreshes a 5-tick caster flag `r_seen` and lobs a hidden
`ParabolicProjectile` at him (`travel_time` 1) whose `end_effects` wait in a `Delayed` of 6 ticks at the landing
point; a check that comes after the runs have stopped - `r_seen` gone, `r_live` still on - removes the flags and
explodes there, 3-6 ticks after the death (all 470 such deaths in 240 logged games). Nothing can be started from a
dead unit, so the spot is armed while he lives. Until 0.50.2 the lob itself flew 6 ticks and its target walked away
from it (below, "Hidden projectiles in flight move the AI"). When Shaco himself dies while it lives, its runs stop
with him (4 such deaths in 28 logged games: no strike, picture or blast after them) - League's clone dies with Shaco
too.

**Every sixth shot a Headshot, trapped champions first (league_caitlyn Headshot).** The attack decides on tick 1
(league_jinx's way) and fires from a `Delayed` (7 ticks, 9 for a Headshot with its own `CasterAnimation passive`). Five
`Permanent` counters `hs_1`..`hs_5`, walked from the top like league_masteryi's Double Strike, make every sixth shot a
Headshot (180% AD; death clears the count, as League's); only plain shots count. While her trap holds a champion (the
`hs_trap` caster flag, as long as the root) a `RandomTarget` on `EnemyChampionInCC` within 1.5x her range (77500: the
radii add 20000) takes the shot instead of the AI's target - League's double-range Headshot on a trapped champion - with
a trap bonus; nothing tells who put a champion in crowd control, so an ally's stun in that window counts too. A net hit
leaves `hs_net` (108 ticks): the next shot is a Headshot. In ten simulated minutes about 29 counted Headshots and 8 on
trapped champions.

**A shot that becomes the net when a champion is on her (league_caitlyn E, 90 Caliber Net folded into the attack).**
The user picked League's E as her escape: on tick 1 of an attack, with E ready (no `e_cd` caster buff, 720 ticks) a
`RandomTarget {range: 25000, casting_target: EnemyChampion}` (about 45000 centre to centre) sets a 1-tick `e_go`, plays
`CasterAnimation e`, fires the net (`TargetProjectile` on `EnemyChampion`: 60 + 60% AD, a 50% slow for 1 s, `hs_net`)
and from tick 7 hops her `MoveBack` 5000 x 6 straight away from that champion (inside `RandomTarget` the hop's target is
the picked unit, league_ezreal E); `SwitchByBuff e_go` then skips the shot. About 2.5 nets a game.

**Three traps on three spots, none thrown at a champion they hold (league_caitlyn W, Yordle Snap Trap).** A `Direction`
cast on `EnemyChampion` (range 80000) with `cooltime_use_count` 3 and cooltime 2160 (a charge every 12 s), on
league_teemo R's slots: the first slot whose `busy` flag is gone takes the throw, a `LinearProjectile` with the trap's view whose
`end_effects` land the trap where it stops - slot a non-penetrating on `EnemyChampion` (it stops on the first enemy
champion on the line: his feet), b and c penetrating with `range` 35000 and 58000 (a `Direction` cast's projectile
stops at caster + direction x range). Thrown at his feet every time (a `Position` cast, the first version) the AI
spent its three charges in a row on one champion and the traps piled up: 19 of 52 pairs alive together lay within
18000 (the user: "会在一个位置无限放夹子 应该错开来放吧"); spread, 11 of 99. The landing adds `alive` for the life
(30 ticks to arm, then 8 s), plays the landing and starts, from a `Delayed` (which keeps the point), a
`RangePeriodProjectile` (radius 9000, `period` 1, the life) on `EnemyChampion` that, while `alive` holds, runs
`RemoveCasterBuff alive` first and then `Bind` 90, the snap picture and `hs_trap`: the removal comes before the next
unit's check in the same tick, so one champion is bitten. Picture links every 15 ticks show the lying trap while
`alive` holds and the fading one as its last link. A zone from `end_effects` outlives its caster (section 5) and her
frozen `alive` cannot be taken, so unguarded it bit every tick while she was dead (285 times in 16 games): the bite
first asks `RandomTarget {range: 1, casting_target: AllyOnlySelf}` for a 1-tick `w_live` flag ("A dead caster").
The AI's champions stand still while they attack, so most traps bite - and a snapped one stands still too: the AI
threw her other charges straight at him, 4.6 throws a game within 2.25 s of a snap, each biting him again when the
root ended (the user: "W敌人踩上去后会连放 这个要改一改 其他时候没问题"). The bite adds `w_hold` for the root and 60
ticks more, and W's effect is `SwitchByBuff w_hold` with an empty branch: the AI scores the branch its buffs pick
(section 3), finds nothing and keeps the charges - 0 such throws; 15 throws and 8.6 snaps a game against 19 and 11.
One charge of 8 s instead ended every back-to-back throw but cost 0.46 kills a game: the AI then threw 10 traps. The held
champion's re-snaps had been worth about 0.55 kills a game; the root back at 1.5 s and the Headshot at 180% won 0.35 of
it back.

**A piercing round at where a champion stood, dodged by stepping aside (league_caitlyn Q, Piltover Peacemaker).** A
`Direction` cast on `EnemyWithoutTower` (range 120000), so it also clears waves and camps; its sound plays on tick 1 and
the shot comes from a `Delayed` 23 ticks later - a `Delayed` keeps a `Direction` cast's direction (no bolt without one in
the logs). Aimed at a champion in reach when it leaves (Morgana Q's `RandomTarget`), it hit almost every time (the
user: "Q是可以躲得 现在百发百命中"). Now the aim is locked 8 ticks before the shot: `RandomTarget {range: 100000,
casting_target: EnemyChampion}` adds a flag and lobs a hidden `ParabolicProjectile` (`travel_time` 8), which lands where
the champion stood; its `end_effects` start the bolt, which leaves from her (every projectile does), heads for that
point and ends there; without a champion the bolt takes the cast's way. The muzzle and the sound stay in the cast's
`Delayed` (a lob landing after her death would play them on her body). Of the bolts aimed at a champion, locked on
tick 1 (League's whole 0.4 s wind-up) 16% hit - the AI's champions keep walking -, 12 ticks before the shot 28%, 8
ticks about 40%. The first unit hit takes 60 + 110% AD and sets `q_first` (40 ticks), the rest 60% of it. Started
from tick 1 the shot comes even when her wind-up is cut short: the same kit with the shot on `start_timing` 24 was
0.6 kills weaker on the same seeds.

**A channelled shot the first champion stops (league_caitlyn R, Ace in the Hole).** A `Targeting` cast on
`EnemyChampion` with a long reach (200000): a crosshair buff on the target for the 1 s channel, league_missfortune R's
crowd-control check every 10 ticks (`RandomTarget {range: 1, casting_target: AllyChampionInCC}` removes the channel
flag), and at tick 61, if the flag holds, a non-penetrating `LinearProjectile` on `EnemyChampion` (speed 20000, radius
8000) toward him: the first enemy champion on the line takes 250 + 150% AD, minions do not block. 4.5 of 5 casts a game
hit a champion. Her laser sight (the user: "女警大招释放时候没有线 ... 中没中 打谁的都不知道") is league_fiddlesticks W's chain
the other way: from tick 10 (the rifle level on tick 12) an `AddCasted` on him (period 2, until the channel's end)
sends every tick, while the channel flag holds, a `TargetProjectile` at him (6000 a tick, the bullet's `y_offset`
-4000: from the rifle) with no effects; its picture is a red dash 2 px thick with its head on the projectile, hidden
5 ticks (past the rifle), then 4 and 8 px long: 6 px apart, the dashes overlap into one line that ends on his pivot (a
homing projectile goes on its target), where the crosshair is drawn now (it sat on his chest, 8 px higher), `z` -1.
The dashes stop when the channel breaks or she fires; the ones in flight run on to him while the bullet follows the
line. The user found it crooked twice ("凯特琳这个大招特效线是歪的？做直了啊", "…连接线特效是歪的 你不修吗"): 24 and 36 px
links, each turned on its own, stepped where two met, and a line from her standing height missed both the barrel and
the crosshair. Short dashes keep a turned line straight: each is too short to step, and their heads lie on the line.

**A cleave every fourth attack or on a timer (league_nocturne passive, Umbra Blades).** League's 12 s cooldown, which
each attack cuts by 1-3 s, comes out at about every fourth attack in a fight. The attack (`start_timing` 1, its hit
`Delayed`) reads a caster buff `p_cd` (720 ticks): while it is absent the attack is the cleave; while it is there,
three counter rungs `p_n1` -> `p_n2` -> `p_n3` (720 ticks each, one removed as the next is added) count the plain
attacks, and the attack that finds `p_n3` cleaves. The cleave removes the rungs, restarts `p_cd`, plays `attack_p` and
on its hit tick a self-only `RangeEffect` (radius 20000, `EnemyWithoutTower`) gives each enemy 120% attack and
Nocturne a `Heal` (15 + 20% AP, `heal_type: Caster`) per enemy hit. The circle reaches a unit's edge, so it takes the
attack's own target even at the attack's full range: in six logged games (about 49 cleaves each) 13% of the cleaves hit
nothing and 20% hit two or more enemies.

**A trail that lies on the ground and follows the champions it hit (league_nocturne Q, Duskbringer).** A `Direction`
cast on `EnemyWithoutTower`: the blade is a penetrating `LinearProjectile` (4500 a tick, 66000; its hit sound plays
once a wave through a 20-tick `q_snd` flag), and a picture-only `LineRangeProjectile` on `Ally` (66000 x 9000, `delay`
300) draws the trail for 5 s without the enemy AI dodging it. The trail's zones: anchors - hidden `LinearProjectile`s
on `Ally` with the blade's speed and ranges 6000, 18000 ... 66000 - each start a `RangePeriodProjectile` (radius 9000,
300 ticks, `period` 6, `AllyChampion`) where they stop, whose application asks `RandomTarget {AllyOnlySelf,
from_projectile: true}` within 9000 whether Nocturne stands in it (league_ekko's pulse). A champion-only twin of the
blade adds an `AddCasted Bleed` (300 ticks, period 6) to every champion it hits, which sends a hidden `TargetProjectile`
at him each period with the same question at 15000: a trail behind him too. Either answer refreshes one `trail` caster
buff (move speed +25%, attack +15%, 10 ticks) by removing and adding it (section 5: same-name buffs add up). In logged
games he stood on a trail about 2 s of the 5 s after each Q (43 a game).

**A tether that fears if it holds (league_nocturne E, Unspeakable Horror).** A `Targeting` cast on `EnemyWithoutTower`
(30000): the links are league_fiddlesticks W's chain (a `TargetProjectile` to the target, a 1-tick
`ParabolicProjectile` landing on him, a `BackToCasterLinearProjectile` flying back at 1600 a tick), one every 12 ticks
for 2 s from one `AddCasted` on the target (period 12, 120 ticks; its `TargetProjectile` leaves from him, as the Q's
champion-trail checks do - a `Delayed` per link wrote the chain ten times, and those kept flying at a target that had
died), with 4 `ApAttack` pulses (20 + 30% AP). After 120 ticks a hidden `TargetProjectile` (100000 a tick: it lands
the next tick) on the target asks `RandomTarget {AllyOnlySelf, from_projectile: true}` within 60000 whether Nocturne
is still near; yes adds a 3-tick caster flag `e_near`, and a `Delayed` of 1 tick reads it: `Fear` (80 ticks) and a
`move_speed_mult` 40 caster buff as long (E's passive, without its direction). The range counts from the champion's
edge (a check at 45000 feared a champion 58932 away, centre to centre). In six logged games 14 of 30 tethers on
champions reached the check (in 10 of the other 16 the target had died first), and 7 feared at 60000, 4 at
45000; at 32000 the check came after most targets had walked out of it.

**A spell shield that pays out when it is hit (league_nocturne W, Shroud of Darkness, folded into E).** The same cast
raises the shroud: a caster buff (90 ticks) with `skill_damaged_reduce` 100 and `cc_immune`, a 1-point `Shield` on
himself (a self-only `RangeEffect`, 92 ticks) and a `WithShield` caster flag `w_guard`. Any hit breaks the shield (a
skill's damage cut to nothing still deals 1, league_fiora W), and a check every 6 ticks from tick 4 finds `w_guard`
gone: one polling zone (`RangePeriodProjectile`, radius 2000000, `period` 6, `AllyChampion`) started where a hidden
1-tick `ParabolicProjectile` lands on the target (a zone starts only from a projectile's end, see section 8); it runs
on every allied champion, and the first check that pays adds `w_done` and `attack_speed_mult` 40 for 300 ticks
(League's doubled passive). W's passive attack speed is in the attack cooldown (48 against the assassins' 50-52). In logged games the
shroud paid out 14-19 times a game, of about 25 casts.

**Team invisibility and a dive from afar (league_nocturne R, Paranoia).** A `Targeting` cast on `EnemyChampion` within
110000: on tick 8 a `RangeEffect` round him (2000000, `AllyChampion`) makes every allied champion, himself included,
`Invisible` for 32 ticks (the flight) and a second one in the dive's `end_effects` 20 more on landing (the burst; the
longer timer wins), and one on `EnemyChampion` gives every enemy champion the `r_dark` mist as long (a picture-only
buff with a `ThreePhase` view); then `MoveToTarget` (3500 a tick, a 45-tick `cc_immune` caster buff for the flight)
lands 120 + 120% attack. The invisibility carries the kit: 4 s +2.12, 2 s +0.12, none -1.86 against the base junglers
(lane 1, seeds 1-12), while halving the passive's heal changed nothing (+2.16); it settled at 3 s. 0.53.2: 3 s outlasted
the 0.75-s ult, so the team stayed hidden with nothing on screen saying why (the user: 「魔腾不放大的时候也全队隐身」) -
now only while the ult plays; that cost 1.2 (+0.84 -> -0.35), which R damage (200 + 150%: -0.62) or a 35 s cooldown
(-0.82) did not buy back, attack did: base 110 and growth 27 (was 100 / 22) +0.88 / +0.61 against +0.84 / +0.99.

**A hook from a raised arm that brings its catch back along its own line (league_blitzcrank Q, Rocket Grab).** A
`Direction` cast on `EnemyChampion` (range 70000) throws a non-penetrating `LinearProjectile` on `EnemyChampion`
(speed 6000, radius 6000, range 78000, `y_offset` -11500): it passes minions and monsters (league_thresh Q). The champion
it reaches takes magic damage and `Stun` 40 ticks. An invisible twin on the same line on `EnemyChampionInCC` lands a
tick later only when the stun took (a Black Shield lets both pass): a 90-tick caster flag `q_held`, the claw on him,
Blitzcrank's `q_pull` loop (60 ticks at most) and the drag. His arm is raised to the shoulder in the strip (League's
pose), 16 px over his pivot, and the hook leaves from there (the user: "从上面勾 别从下面勾"): `y_offset` -11500 starts
it 16500 north of him and it slopes down to his pivot's height at the end of its range (12 degrees), coming down on a
champion's chest; 8 logged games held 76 of 144 hooks, 68 of 125 at `y_offset` 2000 - the slope misses nobody more.
League's hand brings what it caught back along its line onto his arm (the user: "lol里面机器人什么样你就什么样"), but
every `BackToCasterLinearProjectile` flies to his pivot whatever its `y_offset`, under the raised arm. A
`LinearProjectile` thrown in the hook's `end_effects` (behind a `Delayed`) leaves where the hook left and heads for
where it stopped - on the hook's own line, and removed there (the spawn vectors of a logged game; one thrown from the
cast's own `Delayed` follows the cast's direction to the range's end) - so two of them at 1500 a tick carry the way
back: their pictures draw the claw and its chain coming back along the line. A projectile moves on every tick from
the one it is thrown on, so a hook removed h ticks after the throw stopped 6000 x (h + 1) along its line; 13 caster
flags set at the throw, `q_f<j>` lasting j + 3 ticks, are still seen by the hook's `end_effects` j + 2 ticks after it
and by the twin j + 1 ticks after it (4 logged games: every way back matched), so 2 ticks after the stop, and when
the twin lands, the first one still on is `q_f<h>`: it picks the pictures (one pair per h, 0-13) and the drag - `Grab`
1500 with `tick` (6000 (h + 1) + 12000 - 33000) / 1500 (the hook stops 12000 short of a champion's centre), so the
catch stops in reach in front of him (33000 off) just as the claw is back where the strip holds it on his arm (32000
along the line; the picture slows the claw so it slides from the catch's front onto it), when a `Delayed` in the same
branch removes `q_pull` and plays the 8-tick hold (the closed claw on the arm; a `CasterAnimation` holds the caster
from acting). Stopping the catch at the arm's end (43000) with a 12-tick hold cost him about a point (two batches
-0.23 / -0.15 against +0.62 / +1.15): he had to walk before his uppercut.
A miss or a blocked hook brings the open claw back fast. His body only faces left or right while most hooks fly at an
angle (4 logged games: 15 of 80 within 15 degrees of level, 60 between 30 and 90 up), so the claws are drawn over the
units (`z` 1: the catch never hides the claw) and the chains under them (`z` -1), running back to the hook's start:
thrown level his straight arm hides the chain and it comes out of the socket, thrown at an angle it comes out from
behind his head and shoulder - nothing hangs in the air. The flying claw rides the hook, its chain the twin.

**A mark that her next spell bursts, and the Q -> W combo (league_leblanc Q, Sigil of Malice).** A `Targeting` cast
on `EnemyWithoutTower` (70000) throws a `TargetProjectile` (3500 a tick): magic damage and a mark for 210 ticks.
Nothing reads a buff on a target (league_diana Moonlight), so the mark lives on the unit as two `AddCasted`s that
read caster flags: one plays the sigil picture every 12 ticks while the caster flag `q_mark` holds (a 4-frame loop of
3 ticks a frame looks continuous), one checks every 2 ticks for `pop_q`, which every other spell hit of hers
refreshes for 3 ticks (W's blast, the chain and the root, R's versions; R's sigil has its own `rq_mark` / `pop_rq`
and each pops the other): then the sigil bursts on the marked unit (magic damage again) and `q_mark` goes. Any of her
spell hits pops it, not only one on the marked unit, but the AI follows up on the unit it marked nearly always. The
combo (the user: "可以加入连招逻辑 像盲僧那样", league_leesin Q1 -> Q2): a hidden twin of the sigil on `EnemyChampion`
sets `q_champ` when it lands; 24 ticks after the release, with `q_champ` on and W ready (the caster flag `w_cd`, which
W's slot shares: while it runs the slot's effect is an empty branch the AI does not cast, league_caitlyn W), the cast
goes on into W - she dashes onto the champion she marked and the blast bursts the sigil. Without the combo she scored
about 0.6 lower (lane 2 against the five base mages).

**A dash that comes back by itself (league_leblanc W, Distortion).** A `Targeting` cast on `EnemyChampion` (60000):
`MoveToTarget` (4000 a tick) and a blast in its `end_effects` (radius 26000, magic damage, pops sigils). The return is
league_ekko R's anchor: a `LinearProjectile` with speed 1 and range 1 ends where she stood, and its `end_effects` hold
a `Delayed` (75 ticks) that `Teleport`s her back when the caster flag `w_go` is there. The go is queued on her own
unit - a `Delayed` in a self-only `RangeEffect` (`AllyOnlySelf`) - because a `Delayed` queued on a unit that dies runs
only its pictures: queued on the dash's target, the minion the blast killed cancelled 4 of 8 returns. The anchor's
`end_effects` outlive her, so a dead LeBlanc does not come back, and one tick before the return a `RandomTarget` on
`AllyChampionInCC` keeps a crowd-controlled one where she is (league_missfortune R's check; League has no recast while
stunned). A dash cast while a return is pending sets up none of its own: the pending one takes her home.

**A chain folded into the attack that roots if it holds (league_leblanc E, Ethereal Chains).** Every 10 s her next
attack with an enemy champion within 80000 throws the chain at him instead (`CasterAnimation e`, league_caitlyn's net):
the aim locks 8 ticks before the throw (a hidden `ParabolicProjectile` lands where he stood, league_caitlyn Q), and a
non-penetrating `LinearProjectile` on `EnemyChampion` (3000 a tick) flies there through minions: magic damage, the
tether. The tether holds while she stays near: the hit sets a caster flag `e_held` (94 ticks) and an `AddCasted` on
him (90 ticks, period 6) sends a hidden projectile at him each period asking `RandomTarget {AllyOnlySelf,
from_projectile: true}` within 95000 whether she is near (league_nocturne E's check); near - a link flies back to her
(a `BackToCasterLinearProjectile`, 3000 a tick, range 95000), out of reach - `e_held` goes for good: no more links,
no root. Without it the links kept flying to her for the whole 1.5 s after Distortion took her away (the user: "W回本体
有时候没链到特效还在"). After 90 ticks, `e_held` on and her still near: `Bind` 90 ticks and more magic damage. In 8
logged games 37 chains: the links stopped where she passed about 113000 centre to centre (the check counts from the
bodies' edges) and 8 rooted; one `AddCasted` instead of a `Delayed` per link took the attack tree from 391 nodes to
299.

**Repeat the last spell (league_leblanc R, Mimicry).** Each of her spells swaps one `Permanent` caster flag of three
(`last_q`, `last_w`, `last_e`: remove the others, add its own); R is a `Targeting` cast on `EnemyChampion` (70000)
whose effect is `SwitchByBuff last_w -> RW, last_e -> RE, else RQ`: a bigger sigil (its own mark), a bigger dash and
blast (radius 30000) with the return, a bigger chain and root - about double damage. Death clears the flags, so the
first R after a respawn is RQ, as is one before any spell.

**A dodge when she is crowded (league_leblanc passive, Mirror Image).** League's trigger is "below 40% health", which
no effect reads; the user picked "when crowded": while the 40-s caster flag `p_cd` is off, each attack first counts
the enemy champions within 40000 (a `RangeEffect` that sets `p_n1` on the first and `p_n2` from the second,
league_kayle R) and a tick later, with `p_n2` on, she turns `CasterInvisible` for 60 ticks, hops away from one of
them (`MoveBack` 6000 a tick for 4 ticks inside a `RandomTarget`) and leaves the clone picture where she stood; the
shot is skipped.

**Overdrive folded into the uppercut (league_blitzcrank W in E, Power Fist).** W's cooldown is a caster flag `w_cd`
(900 ticks). Every action asks first: with `w_cd` absent and an enemy champion within 60000 (`RandomTarget` sets a
1-tick `w_go`), Overdrive starts - move speed +20% for 240 ticks and +20% more for the first 120 (two caster
buffs: League's speed decays), attack speed +25% for 240, the steam from both smokestacks each second (a
self-only `RangeEffect` holding `Delayed` caster pictures), then a 25% self-slow for 90 ticks. The uppercut itself is
`skill2`, a `Targeting` cast on `EnemyWithoutTower` (lanes and camps): an enemy champion within its 25000 reach is
punched first (a `RandomTarget` that also sets a 1-tick `e_aim` flag so the cast target is not hit as well), else the
cast target - physical damage and `Airborne` 60.

**The ult's passive while it is ready, the armed active with a silence (league_blitzcrank R, Static Field).** The
attack carries, while the caster buff `r_cd` is absent, an invisible `TargetProjectile` on `EnemyWithoutTower` (no
towers): a static mark on the unit hit and a `Delayed` 60-tick lightning bolt of magic damage. The ult is armed like
league_taric's and league_riven's: the slot (a 3-tick `None` action on the `idle` tag) arms `r_armed` for 600 ticks and
every action plus a pulse every 15 ticks fires it when an enemy champion is within 30000: `CasterAnimation ult` (35
ticks), the charge picture, and on tick 23 (the strip's burst frame) the field round him - magic damage on
`EnemyWithoutTower` within 40000 and `BlockSkill` 60 ticks (League's silence) on the champions - and `r_cd` for the
ult's cooldown (3000 ticks), which stops the passive until the cooldown ends, as in League. Left unused, a 3-tick
`ult_cooldown_mult` 4900 refunds it.

**A shield when in danger instead of at low health (league_blitzcrank's passive, Mana Barrier).** Nothing reads
current health, so danger stands in: two or more enemy champions within 35000 (a `RangeEffect` whose every hit
climbs a 3-tick `mb_n1` -> `mb_n2` ladder) or Blitzcrank himself crowd-controlled (`RandomTarget` `AllyChampionInCC`
within 1 finds only him, league_missfortune R), with the 3600-tick `mb_cd` off: a self-only `Shield` of 120 + 80% AP
for 600 ticks and a `WithShield` caster buff that carries its picture (it goes when the shield breaks, section 5).
The check runs at every action and on a train of pulses queued on himself (every 30 ticks for 240 ticks after an
action, one train at a time): a stun stops his actions, not the pulses, so a hook or a stun in a fight still sets it
off. About 3-4 shields a game in the simulation.

**A field fixed where she landed: the target stays in, she may leave (league_camille R, The Hextech Ultimatum).** A
`Targeting` cast on `EnemyChampion`: a 14-tick caster buff (`damaged_reduce` 100, `cc_immune`) for the leap and, from
tick 5, `MoveToTarget {speed: 5000}` whose `end_effects` set `r_on` (180 ticks), knock the others back (the target keeps
its place through a 2-tick `cc_immune`), 3 ticks later start an `AddCasted` (`Bleed`, period 1) on the target, and fire
an anchor - a `LinearProjectile` with `speed` 1, `range` 1 and `y_offset` 5000 (league_ekko R; at `y_offset` 0 it started
5000 over her and took 5000 ticks to come down) - whose `end_effects` start the zones there (180 ticks, period 1): the
drawn arena's floor as a `Rect` on `EnemyChampion` (a 2-tick `r_tin`), a circle of 30000 on `AllyOnlySelf` (a 2-tick
`r_cin`: she is in) and a map-wide circle on `AllyOnlySelf` that removes `r_on` whenever `r_cin` is missing - League's
"ends automatically within 1 second if Camille leaves the area or dies" (the user, 2026-10-03: "敌人不能出去但是自己可以
出去"; until then that zone held a `Pull`, which brought her back to the centre - a `Pull` in a projectile's
`applied_effects` heads for the projectile, section 4 "Pull vs Grab" - the user had asked for "卡密尔的大招是无法离场的").
With her radius the circle lets her stand about 46000 from the centre: at 24000 (about 40000) she "left" while kicking a
target at the arena's edge; 30000 and 36000 ended the same share of arenas by her walking off (about a quarter: the AI
going for someone else or leaving), and the smaller one keeps the pull toward her near the arena. The target's
`AddCasted` asks every tick, while she lives (`RandomTarget {range: 1, AllyOnlySelf}` -> a 1-tick `r_live`) and `r_on`
lasts: a 2-tick `BlockMoveSkill` (no dash; a 177-tick block from the landing outlived an arena that ended early), his
mark as 30-tick `AddBuff` pieces behind a 30-tick caster flag (`r_mk`), and no `r_tin` -> a 1-tick `Grab` (2000) toward
her, the wall's zap at most every 30 ticks. `r_tin` is any enemy champion in the arena, his teammates too, so a safety
net also pulls him when she is not within 47000 of him (`RandomTarget AllyOnlySelf` from the projectile; with her body
about 62 px between the centres, more than the arena is wide, so it never touches a target still inside - at 28000,
43 px, it nudged him in 7% of his ticks inside: the user, "离她太远不是应该不能释放吗？为啥强行？"). `Grab` and `Knockback`
only pull toward or push away from the caster, so the target is kept through her - and the arena has to end when she
leaves, or it would drag him after her. Her E in the arena hooks only to escape: `SwitchByBuff r_on` stands before the
engage search (a hook out would end the arena and free the target), the outnumbered escape stays on. In 24 simulated
games (103 arenas) 30 ended by her walking off, 32 after the target died and 2 by her death.
The first field let the target walk out (the user: "敌人也不能走出那个圈 现在还可以走出去"): a 36000 circle checked every
6 ticks, and a shape counts the unit's own collision radius, so the target's centre had 51 px round the landing point
while the arena is drawn 66 x 30 px - the ground has no perspective squash (the 5v5 map is a square, 960000 units, a
1280 px picture; the base game's area pictures are round). In twelve simulated games the target stood outside the
drawn floor 58% of the R ticks; with the box, every tick, the centre pull and the safety net 2%, mostly against
the wall. A `Rect`'s `width` and `height` are whole sizes with the unit's radius added round them (her `r_cin`
flipped at about 23500 across with `width` 15000, and at 15800 up and down with `height` 0). The arena's picture is
drawn 5 px higher than the rings (`import_camille.py` `FLOOR`), so its floor - back wall to front wall - is centred on
the zones. Her E can't cut the leap either (the user: "青钢影的大招时没法躲避的"): E's pulses run beside her actions, and a
hook that pulled her mid-leap once left the ult landing nowhere; `r_leap`, from the cast to the landing, stops E's
throw, pulls and E2. An anchor fired on tick 14 of the action instead (to time the picture) was skipped whenever the
leap landed later: the AI leaps from about 52000 centre to centre.

**A zone's picture comes turned by its direction (league_camille R).** The anchor flies 1 unit, so its direction
is (0, 0), and the `RangePeriodProjectile` it starts got (-1, 0) in every logged field (15 of 15). A zone's view is
turned to its direction like any projectile's - here half round, upside down - so the sheet stores the arena's frames
turned half round and the engine turns them back (`tools/art/import_camille.py` `TURNED`). A picture cannot be stopped,
so one that ends with the arena comes in 30-tick pieces: `r_field` (the arena forming, 500 ms) at the landing, then five
`r_floor` pieces (`r_zone`, the standing arena's 500-ms loop) every 30 ticks, each behind `SwitchByBuff r_on` and an
alive flag (a dead Camille keeps `r_on`, but no flag can be added to her). Zones started from a `Delayed` in the anchor's
`end_effects` got (1, 0) or (-1, 0) by the side she stood on (266 of 294 pointed from her to the zone): every other
piece upside down. Started from a projectile fired at the landing they get its (0, 0) like the anchor's own zones, so
each piece rides a clock - a `LinearProjectile` like the anchor with `range` 30, 60 ... 150: with direction (0, 0) it
stays on the spot and ends after `range` ticks (320 pieces logged, all (-1, 0), all on the landing point).

**A hook that needs a hold, armed by its slot and thrown by pulses (league_camille E, Hookshot).** League's
Hookshot needs a wall; TFM2 has none (section 4) and no casting target picks towers alone. The user's rules: minions,
monsters and towers hold, champions never ("拉英雄直接设置落空"), no casts at champions for nothing ("你可以加连招逻辑啊
这样就不会无脑E英雄了") and an escape too ("逃跑时也可以放吧"). Cast from the slot on a champion, the search below found no
hold near it at 41 of 69 casts (fights away from the waves) and the cooldown went on a miss; cast on `Enemy`, the AI
threw it at champions 11 times a game. So the slot is a 3-tick action on the `idle` tag (`Targeting EnemyChampion`,
range 60000, cooltime 240) that adds a 240-tick `e_armed` flag and an `AddCasted` (`Bleed`, period 6, 240 ticks) on
her own spot through a self-only `RangeEffect`: its effects run every period with her as the caster and her position
as the origin - a pulse train with the search written once (league_fizz E's pulses rode a zone). A pulse, armed and
without the 720-tick `e_cd`, picks a unit with `RandomTarget` on `Both` - minions, monsters (the epic monster too),
towers and champions of both sides - and sends the pick two twins, one on `Both`, one on `BothChampion` that flags a
champion (both hit in the same tick, the champion one's effects after the other's: league_ezreal Q); a tick later a
pick that holds starts `e_cd`, plays `CasterAnimation skill2` (the throw) and 8 ticks later sends the hook (a
`TargetProjectile`) at it, whose applied effects pull her there (`MoveToTarget`). Engage: a champion within 60000, a
pick within 35000 of it (`from_projectile`) that is within 60000 of her (a `RandomTarget AllyOnlySelf` from the pick),
then E2 from the hold. Escape, while outnumbered by two (league_kayle R's count ladder: two enemy champions within 45000
and no ally within 40000, or three and one) and not in her R: a pick within 60000 of her with no enemy champion within
40000 of it, at least 25000 from her; E2 is a `MoveBack` (4500 x 8) from an enemy champion near. One pick a pulse:
five engage and six escape picks a pulse (every 10 ticks) made `skill2` 438 effect nodes, and the game copies the
whole `skill` and `skill2` of every mod champion every tick of a shown match (the performance work's measurement:
cost in proportion to their nodes); one pick every 6 ticks is 116 nodes and landed more E2 stuns in twelve simulated
games (117 against 101). Nothing reads health, so being outnumbered stands
for fleeing; after the escape the AI walks back when it wants the fight. Hooked in four games: 38 minions, 3 monsters
(stump, serpent, epic), 1 tower. With the final numbers, twelve simulated games: 10.4 throws a game, 10.2 pulls, 8.2 E2 stuns, no champion hooked and no empty throw; 0.1-0.4 escapes a game (ganks seldom happen next to a hold).

**A charged-attack cue that a dying target cannot cancel (league_camille Q2, Precision Protocol).** League lights
her leg blades once the second kick is charged (the user asked for it). The engine plays `idle` and `run` itself, so
the cue is a buff's picture: `q2_ready` (a caster flag) from the charge's end to the charged kick, a `ThreePhase` view
(`pre_tag` the flash as the charge completes, `loop_tag` the blades' bloom, `remove_tag` the bloom draining as the kick
goes off; league_janna's storm shield). A buff's picture is not mirrored when she faces left (section 6), so the cue
is symmetric about her pivot: a soft cyan bloom over both blades (partial alpha, as league_ekko's R ghost) with hard
sparks. The flag is set by a `Delayed` of the charge's 90 ticks from the first kick - and a `Delayed` in the kick's
own effects did not run when the unit kicked died before it (a minion: 1 of 4 charges in a logged game showed no
cue); riding a self-only `RangeEffect` (`AllyOnlySelf`) on her, 36 of 37 charges lit up, the last one cut by the
game's end.
**A sweep's outer edge (league_camille W, Tactical Sweep).** No shape is a ring sector, so the outer edge is a disc
ahead: next to the cone (`DirDot`, radius 46000, range 700 - about +-45 degrees) a `RangeEffect {Circle 4000,
Forward offset 36000}` gives the units at the cone's rim the % max health damage, the slows and, on champions, her
heal. The sweep's picture is a `LineRangeProjectile` (60000 long, nothing applied, 23 ticks) whose crescent is drawn
with the fan's point 30 px behind the line's middle - the line starts at her.

**Stacks that rupture at the fifth hit, counted on her (league_kaisa passive, Second Skin).** Nothing reads a buff
on the target, so the Plasma count lives on her as league_vayne's Silver Bolts does: four caster flags `pl_1` ->
`pl_4` (each 240 ticks, the step removing the one before it). Her attack fires the real bolt (`Enemy`) and a
champion-only twin with the same speed and `y_offset`, so they land on the same tick and the twin's `applied_effects`
run only on a champion: they walk the ladder from the top (`pl_4` ruptures - a `FixedAttack` of a flat part, a share
of her attack and a share of the target's maximum health, League's missing-health share being unreadable - else the
next flag), each step with its magic damage and the mark's picture (`pl_1`-`pl_4`, the pips drawn as 2 x 2 squares so
the count reads at game size). A third twin on `EnemyChampionInCC`, a tick later and without damage, climbs once more:
League's allies' immobilising effects. W climbs two steps at once (three evolved) in one chain - `to(k)` is the flag
`pl_{k+n}` or the rupture - instead of nested climbs, since the engine copies a skill's tree every tick. About 2-3
ruptures a game in the simulation.

**Supercharge folded into the attack (league_kaisa E).** League's E (move speed while charging, then attack speed) is
one decision in the attack: without the 480-tick caster buff `e_cd` and with a `RandomTarget {EnemyChampion}` within
75000, the shot also sets `e_cd`, a move-speed flag (`move_speed_mult`) for 66 ticks and, `Delayed` by those 66, an
attack-speed flag (`attack_speed_mult`) for 240 ticks; the arcs on her are 1 s pictures queued every 60 ticks behind a
`SwitchByBuff` on that flag. The evolved E (level 9) adds `CasterInvisible` for 30 ticks. The `Delayed` attack
speed and arcs sit in a self-only `RangeEffect` inside the `RandomTarget`: left in the `RandomTarget` they waited on
the picked champion and were dropped when he died first - a kill right after the E (her R in, the rupture) lost the
whole attack speed (SDK simulation: `e_ms` ran out and no `e_as` came).

**A volley split among the enemies round her, fanned out of the pods (league_kaisa Q, Icathian Rain).** The first
missile flies at the cast's target; the rest come from three `AddCasted` on herself (a self-only `RangeEffect`), whose
`effects` run on her each period: a `RandomTarget` (`EnemyWithoutTower`, 60000) and a homing missile from her at the
picked enemy, so an isolated champion takes them all and a wave splits them. A casted fires once every `period` after
its first, `duration / period - 1` times (the first test fired five of six); the three are `Delayed` 0, 2 and 4 ticks
with a 6-tick period and each lifts its missiles to its own height (`y_offset` -24000, -15000, -33000: the pods, and a
row of lasers under and over them), so the lasers fan out and meet on the targets - League's swarm, which the engine
cannot curve. 6 missiles, 12 once evolved (9.7 a cast over a game: the evolution comes at about 4 minutes).

**Evolutions by attack and level (league_kaisa Living Weapon).** Nothing reads attack or level directly, so
league_tristana's probe reads them: under a 3-tick 99% `damaged_reduce` she shields herself (a 3-tick `Shield`) and
hits herself with a `FixedAttack` 100 times what the shield is measured against - `attack_ratio` for Q's evolution
(the shield is 20% of 199.5: her hit breaks it once her attack is 200), `hp_ratio` against the level table's maximum
health for E (level 9) and W (level 12); a `WithShield` flag gone two ticks later means the hit broke the shield, and the
stage becomes a permanent flag (two passes in a row in a fight, a silent re-read at each life's first cast: death
clears caster buffs). The probes run in Q (a skill: no crit roll on the self-hit). A hit that breaks the shield
spills the rest into her health: 4-50 a probe, more with health items, and a 250-340 number over her on every Q
(players: 「卡莎的q有点bug 这么q消耗自己的血」, 2026-10-04). Now a 1-tick soak shield (1000000) follows each probe's
shield - shields are spent in order and the soak is gone by the end of the tick (section 5, "`WithShield` to the
tick"), so the flag still reads the probe's shield alone - and the hit is small: 5% of her attack against a shield of
10, 2% of her maximum health against 32 (level 9) and 37 (level 12), `ceil` of the stat at the threshold since the hit
is floored; one probe every 15 s instead of 5. Two 18-minute simulations: no health lost to a probe (10 times before),
the stages at the same levels. league_tristana's probes took the same soak, 2% hits (shields 27 / 32 / 37) and 15 s (2026-10-05: no health lost in two games, 7 and 4 times before); league_kayle's took the soak alone (tools/fix/fix_kayle_probe.py: 60 probe shields; 10 and 9 losses -> 0) - her probes have no damage guard, so a smaller shield would break under an enemy's ordinary hit.

**A dash to a damaged champion, then a shield (league_kaisa R, Killer Instinct).** A `Targeting` cast on
`EnemyChampionRecentlyAttacked` (100000): the action lasts only the 8-tick launch; at tick 7 the launch burst is left on
the ground (a caster view, not following), the dash pose is forced (`CasterAnimation ult_dash` for the longest flight)
and `MoveToTarget` (6000 a tick) takes her onto him; its `end_effects` remove the dash pose, force the landing
(`ult_land`) and shield her for 2 s. League's R needs Plasma on the target; gated on her Plasma flags the AI still cast
it with the branch empty (a wasted ultimate in 2 of 4-5 casts: it scores the cast, not the branch), so "recently
damaged by her team" stands in. Dashing in from 150000 she died 2.6 times a game; from 100000 with a larger shield 2.1,
the same as a variant that stopped 45000 short of him (a streak and a `Teleport`), so the dash stays: her body flies.

**Three spells, then a chord by the last song (league_sona passive, Power Chord).** Every spell counts one on a ladder
of `Permanent` caster flags (`pc_1`, `pc_2`; the third adds `pc_ready` and the glow picture; W with E counts two, and
while the chord waits a spell only refreshes the glow - in League it does not stack) and swaps one `Permanent` song
flag of three (`song_q` / `song_w` / `song_e`, the last one cast; league_leblanc R's way). The attack decides on tick 1
(league_jinx's way): with `pc_ready` on it plays its own strip (`CasterAnimation attack_p`) and sends the gold note on
tick 11 with a hidden twin on `EnemyWithoutTower` (in League any unit but a tower uses the chord up) whose effects are
`SwitchByBuff song_e -> Tempo, song_w -> Diminuendo, else Staccato`: bonus magic damage, doubled (Staccato), the
target's `attack_mult` and `magic_power_mult` -25 for 3 s (Diminuendo), or a 40% slow for 2 s (Tempo); a self-only
`Delayed` 1 in it removes `pc_ready` and the glow, so every unit the same note reaches that tick still gets it. In 3
logged games about 20 chords a game: 13 Staccato, 7 Tempo, Diminuendo almost never (half her W casts bring E, which
is then the last song).

**Auras that follow her and bless each ally once (league_sona Melodies, on Q, W and E).** An `ApplyInProjectile` with
`follow_caster: true` in the `Targeting` cast (`tick` 180, a 45000 circle, `applied_target: AllyChampion`) spawns on
her and moves with her for 3 s; each allied champion it touches (her too) gets the song once: Q's +15% attack and
ability power for 3 s, W's shield and its `WithShield` picture, E's speed. Its picture is the zone's own
`view_projectiles` entry (`repeat`, `z` -1), so the ring rides under her feet. On `AllyNotSelf` E's first aura sped
her minions and towers too (section 3).

**Two bolts at the first two enemies, champions first (league_sona Q, Hymn of Valor).** A `Targeting` cast on
`EnemyWithoutTower` (65000, lanes and camps); one `RangeEffect` round her on `EnemyWithoutTower` visits the units in
entity-id order (champions first) and a `SwitchByBuff` on two caster flags (`q_n1`, `q_n2`, 2 ticks, removed at the
cast) sends a homing note at the first two only. 3 logged games: 46 casts a game, 72 notes, 15 on champions.

**A heal for her and one ally, E on its own timer (league_sona W, Aria of Perseverance with Song of Celerity).** A
`Targeting` cast on `EnemyChampion` (80000: only in fights): a self-only heal and a `RandomTarget AllyNotSelf` heal
(60000; nothing reads health, League picks the most wounded), the shield aura; E rides in the same cast when its
caster flag `e_cd` (840 ticks) is off - the haste aura, a self-only +10% on top of the aura's +20%, a second count and
the last song.

**The ult's passive after its first cast (league_sona R, Crescendo with Accelerando).** A `Direction` cast on
`EnemyChampion` (75000): a penetrating `LinearProjectile` (5000 a tick, 95000 long, radius 20000) on `EnemyChampion` -
magic damage and `Stun` 90. The same cast adds a `Permanent` caster flag `r_haste` once per life: `skill_cooldown_mult`
25 (Q and W capped at 80% of their cooldown) with `ult_cooldown_mult` -25, so the ult's own cap stays (section 5:
the ult's cap adds both). 3 logged games: 2.7 casts a game, about one champion stunned a cast.

**Marks counted on him, the third stuns (league_kennen passive, Mark of the Storm).** Nothing reads a buff on the
target, so the count lives on him (league_kaisa's Plasma): two caster flags `k_1` -> `k_2` (360 ticks, refreshed by
each new mark). Every champion hit of his spells (and of every fifth attack) runs one `mark()`: with `k_2` on, the hit
stuns that champion (`Stun` 75 ticks, 30 while the caster flag `k_recent` says he stunned someone in the last 420 -
League's shorter second stun), plays the stun picture and sets `k_boom`; else it shows the pips over the head (one or
two lit). The count itself moves a tick later in a `Delayed` queued on him (`AllyOnlySelf`: queued on the champion
it would be dropped if the hit killed him): it climbs, or after a stun clears and sets `k_recent`. A 2-tick lock per
source (`k_lock_q` / `_w` / `_a` / `_r`, E's for the whole rush) counts one cast once however many champions it hits,
and every champion a stunning cast reaches is stunned - League gives each of them a mark. Only champion hits count
(the user's pick). The count is his, not theirs: a mark on one champion and two on another stun the second.

**A skillshot through the wave to the champion (league_kennen Q, Thundering Shuriken).** A `Direction` cast on
`EnemyWithoutTower` (80000). Two ticks into it a `RandomTarget` on `EnemyChampion` sets the 11-tick flag `q_aimed`
and throws a hidden `ParabolicProjectile` (8 ticks) where the champion stands; its `end_effects` throw the shuriken
at that point (league_caitlyn Q's aim lock: a champion who keeps moving steps out of it) - a non-penetrating
`LinearProjectile` on `EnemyChampion` that flies past the minions to the first champion on its line. Thrown at the
cast's way without a champion (`q_aimed` off), it is a `LinearProjectile` on `EnemyWithoutTower` for waves and camps,
with a champion-only twin that reads the real one's 1-tick `q_now` flag (league_ezreal Q), so only a champion it
really hit gets a mark. On minions' targets the aimed throw reached a champion 3-7 times in 45-61 a game; through
the wave, with a radius of 7000 at 8000 a tick, 42% of the aimed throws hit. The combo Q -> W (the user: 连招): the
champion hit sets `q_near` (a `RandomTarget` on `AllyOnlySelf` from the projectile within the surge's 50000) and 4
ticks later, on him, with `q_near` on and the surge's cooldown flag `w_cd` off, Electrical Surge follows.

**A third basic without a slot (league_kennen W, Electrical Surge).** Q and E take `skill` and `skill2`, so W is
folded in twice. Its passive is the attack's count (league_masteryi's chain): four caster flags `a_1` -> `a_4` (600
ticks), the fifth throw the charged star - extra magic damage and, through a champion-only twin of the star, a mark
(its own flash and hit). Its active is a function the other spells call - after a Q hit on a champion near him and
at the end of E's rush - on its own 540-tick caster flag `w_cd`, spent by whichever comes first: the pose at once
(`CasterAnimation w`), 6 ticks later the burst (radius 50000, the ring round him from the big sheet): magic damage to
every enemy and a mark on the champions.

**A rush through enemies that ends in two follow-ups (league_kennen E, Lightning Rush).** A `Targeting` cast on
`EnemyWithoutTower` (50000): `RushTime` (2500 a tick for 16 ticks, `penetrate`, radius 15000) toward the target and
through it - magic damage to every enemy passed, and a mark through a `RandomTarget` at range 1 on `EnemyChampion`
(a minion's hit cannot mark). The lightning-ball picture rides him (a caster view, z 2, over the crouched dash pose).
The end, 17 ticks later, is a `Delayed` queued on him, not on the target: queued on a minion the rush killed it ran
only its pictures - no attack speed, no `w_cd`, no `r_cd`, and the storm came again on the next rush. It gives 50%
attack speed for 4 s, breaks the ball, casts the surge if `w_cd` is off and runs the combo E -> R (the user: E
冲进人群时如果大招好了就直接接 R): with the ult unlocked (`r_open`, a `Permanent` flag the ult slot's every cast sets)
and unused (`r_cd`) and an enemy champion within the storm's radius, the storm starts; the ult slot then finds
`r_cd` and goes out empty, which starts its own cooldown ("A flag does not hold every slot").

**A storm that follows him, as one casted on himself (league_kennen R, Slicing Maelstrom).** A `None` cast on
`EnemyChampion` (55000; League's radius is his attack range: at 45000 the storm missed champions he fought at 73000
centre to centre): the caster flag `r_cd` (3000 ticks), +25 armour and magic resistance for 181 ticks, the storm's
picture (a 2.9 s caster view that follows him, under the units) and one `AddCasted` on himself (duration 151, period
30): each period a `RangeEffect` round him on `EnemyChampion` within 55000 - magic damage, the bolt and a mark (one
per strike), so the third strike stuns everyone inside. One strike in the tree is enough for both callers (the ult
and E's combo; the game copies `skill` and `skill2` every tick: E stays at about 160 nodes); his death clears it.
**Marks a later hit sets off on every marked enemy (league_ryze Spell Flux and Overload).** League's Flux sits on
the enemies and Overload bounces to the Flux'd ones; nothing reads a buff on another unit, so each mark is an
`AddCasted` on the enemy that reads the caster's flags. E's zone (a hidden 1-tick lob onto the target, then a
`RangeProjectile` on `EnemyWithoutTower`) gives every unit it reaches two of them: one plays the mark's picture every
12 ticks while the caster's generation flag (`fx_c`, 240 ticks) holds, one checks every 2 ticks for the caster flag
`q_pop`. Q's hit raises `q_pop` for 3 ticks and queues on the caster the removal of the generation and of `q_pop`:
every marked unit bursts once in that window (405 bursts counted in the logs, none twice), and the generation is
used up. Two generations (`fx_c` from the combo's E, `fx_r` from R's landing E) let a new E switch the other off,
so a unit never carries two live marks. The wider spread for a target already marked (38000 against 25000) reads a
flag set before the generation is refreshed - read after it, every E took the wide zone.

**League's combo as one cast (league_ryze E -> W -> Q).** Ryze's W and E reset Q, so League players cast E, W, Q
in a row; `skill2` is that sequence on one `Targeting` cast (60000, `EnemyWithoutTower`): E on tick 6, W on 24,
Q on 38 of one 12-frame strip, the W and the Q `Delayed` on the target with a flag set on the caster
(`c_w_ok`, `c_q_ok`): a `Delayed` queued on a unit that dies runs only its pictures, so when the target died the
caster's own `Delayed` checks find the flag missing and fire the W or Q at a `RandomTarget` (champions first). The
runes League's Q passive counts are pictures and flags on the caster (E -> one, W -> two, Q spends them: move speed).
2026-10-05 (the user: 「没有高爆发的连招 查查高手怎么玩的」): high-elo Ryze chains Q between every E and W (Q-E-Q-W-Q-E-Q), so the cast is now
E -> W -> Q -> E -> Q on ticks 6/16/26/36/46; the second E and Q go only at the cast's target (a fallback for each put the
tree at 515 nodes). The second E is a third Flux generation (`fx_d`) so the first E's marks never burst twice, and one
`fx_any` flag stands for "any Flux up" - three nested `SwitchByBuff`s on the generations had copied every `yes` branch
three times (skill2 241 nodes, skill 23).

**A team teleport to chase or escape (league_ryze R, Realm Warp).** The user: never at an enemy already in front of
him, "追敌人或者逃跑用", "或者运送小兵". The first version - a `Direction` cast on `EnemyChampion` (80000) that blinked 30000
ahead (`DirTeleport`) - went out in 163 of 163 simulated casts with the nearest enemy champion 30000-55000 away, inside his
attack range: the AI decides an ult like that once the fight is on, and 45 landings ended within 30000 of an enemy. The slot
now only arms R (league_riven R: a 3-tick `None` action on the `idle` tag, `EnemyChampion` within 120000, `r_armed` for 600
ticks, left unused a 3-tick `ult_cooldown_mult` 4900), and an `AddCasted` on himself (period 10) checks while armed:
- escape: two enemy champions within 30000 (league_kayle R's `n1` -> `n2` ladder in a `RangeEffect`), or one within 15000 (a
  `RandomTarget`) with no `AllyNotSelf` within 50000. `RandomTarget EnemyChampion` within 30000 holds the jump: after the
  60-tick channel a `MoveBack` (15000 x 4) straight away from the champion it picked - it runs from a `Delayed` queued on
  that champion, so the direction is taken at the jump. A projectile cannot fly the other way to show the far portal during
  the channel: a `LinearProjectile`'s `speed` is unsigned too (`-10000` fails to parse and breaks the kit, like
  `DirTeleport.moved`), so the escape's arrival is drawn when he lands.
- chase: no enemy champion within 45000 (his reach) while one was within the last 90 ticks (a `r_seen` refresh), an
  `AllyNotSelf` within 50000, and a `RandomTarget EnemyChampionRecentlyAttacked` (it works in a `RandomTarget`) within 100000:
  a hidden, non-penetrating `LinearProjectile` on `EnemyChampion` toward it (speed 26666, range 80000, radius 5000) stops
  where it touches the first enemy champion, plays the far portal there, and a `Delayed` in its `end_effects` `Teleport`s
  him there at the end of the channel (the stop point is kept, section 4). A radius of 40000 landed him an attack range
  short - by then the fleeing champion had run another 60000 (1000 units a tick): after the landing 41% stood in his reach,
  with the portal on the champion 62%.
Requiring an ally near the chase (he follows with the team, never alone at low health) and the "one in reach a moment ago"
check (no chase on the approach - the first try warped onto five enemies walking in) came from the logs. Every allied
unit in his portal comes along: an anchor (league_ekko R) at his feet starts, after the jump, a zone on `AllyNotSelf` whose
applied effect is a `TargetProjectile` on `BothWithoutTower` carrying `Grab {speed 15000}` - a `Grab` straight from a zone
on `Ally` or `AllyNotSelf` dragged two allied towers across the lane in the simulation (`tower` 6 from 368000,592000), and
no casting target names allied minions alone. Crowd control breaks the channel (a `RandomTarget AllyChampionInCC` on
himself every 15 ticks sets `r_cut`). In 72 games: 2.2 chases, 0.6 escapes and 0.2 cut channels a game, a chase carrying about 0.8
champions and 0.2 minions; lane 2 +1.41 / +1.35 against +1.65 / +2.01 for the old blink (it threw its landing
Spell Flux into every fight).
2026-10-05, the user: 「团战开了大往里面送」. Logged landings (a test runner that tags each jump after the `ult`
animation, 240 games): 16% within 20000 of an enemy champion, 17% with two within 45000, 40% with no ally within 50000,
16% dead within 3 s. The chase now lands r_stop 38000 short of the first enemy champion on the line (inside his reach,
not on it), needs an `AllyNotSelf` within his portal (25000, so someone comes along) and is skipped when three enemy
champions are within 100000 of him (a teamfight - the escape still runs): 8% / 8% / 14% dead, 1.8 chases a game.

**Four shots, the fourth a crit, then a reload he walks through (league_jhin, Whisper).** The attack is a chain of
three caster flags `a_1` -> `a_3` (600 ticks); the fourth plays its own strip (`CasterAnimation attack4`) and fires
on tick 12: a 1-tick `crit_chance` 100 caster flag before its `Attack` crits it (a `BaseAttack` crits; an `Attack`
in a `Skill` action never does), `RemoveCasterBuff` before the second `Attack` (10% of maximum health) keeps that one
plain. The reload is a self-only `RangeEffect` with `BlockAttack {tick 130}`: an `attack_speed_mult` debuff does not
delay the next attack (its cooldown is fixed when an attack starts, simulation log) - blocked, he walks and casts
through the 2.2 s, +25% move speed for 2 s. The bullets are `TargetProjectile`s lifted to the muzzle of their shot
frame (`y_offset` -2000 / -2500: 5000 - y_offset above the pivot), their views opening on an empty tick.

**A grenade that hops among enemies but never back (league_jhin Q, Dancing Grenade).** `RandomTarget` with
`from_projectile` picks the unit the projectile just hit (a monk hopped onto itself in the simulation), so the hops
come from league_missfortune Q's wide twin: a penetrating `LinearProjectile` on `EnemyWithoutTower` (25000 wide,
140000 long, the grenade's speed) launched with the homing grenade. The grenade's hit opens a 12-tick window flag on
him (and a 1-tick `q_wait` so the units the twin touched before the hit do not count); every unit the twin touches
inside the window takes one hop - a drop picture and, 6 ticks later, the hit - up to three, counted by caster flags
`q_h1` -> `q_h2`. The +35% a kill reads a kill flag on each unit hit (`k_read` ticks later, the league_jinx check) and
climbs a ladder `q_x1` -> `q_x3` on him. 25-45% of the casts hopped in the simulation, none back onto the unit hit.

**A long shot that roots the champions his team hit (league_jhin W, Deadly Flourish).** A `Direction` cast on
`EnemyChampion`: 36 ticks in, a `RandomTarget` on `EnemyChampionRecentlyAttacked` (a champion in the fight; else any
`EnemyChampion` in reach) throws a hidden 6-tick `ParabolicProjectile` where he stands (league_caitlyn Q's aim lock),
whose `end_effects` launch two `LinearProjectile`s down that line: a twin on `EnemyChampionRecentlyAttacked` that
refreshes a 2-tick caster flag `w_rec`, and the shot on `EnemyChampion` (it stops on the first champion): damage, then
a `Delayed` of 1 tick roots him if `w_rec` or `w_mark` (Jhin's own hit on a champion in the last 240 ticks) is on -
the engine runs the two projectiles in either order, so the shot reads the twin a tick later.
`EnemyChampionRecentlyAttacked` works as a projectile's `applied_target` (its window was not measured).

**A trap thrown before the shot, and a bloom where he kills (league_jhin E, Captive Audience, in W).** With the
15 s caster flag `e_cd` off, W first lobs the lotus (`ParabolicProjectile`, 18 ticks) at a champion within 75000.
Landed: its picture, a caster flag `e_alive`, and 24 ticks later a `RangePeriodProjectile` trigger on `EnemyChampion`
(period 1, 300 ticks) - started from `end_effects`, it outlives a dead caster, so it first asks whether he lives
(`RandomTarget` `AllyOnlySelf` at range 1 finds no dead caster). The first champion on it blooms it where he stands: a
1-tick lob onto him from a `Delayed` (no projectile spawns straight from a zone's applied effects), whose landing runs
the bloom (picture, a slow zone, and 120 ticks later the burst zone). The passive: every shot of the attack, W and R
also fires a hidden lob landing where the target stood 10 ticks later; 8 ticks after it lands it reads that source's
kill flag (`k_a` / `k_w` / `k_r`: set on the champion's hit, cleared by a 3-tick casted while he lives - league_jinx,
league_tristana) and blooms on the corpse. A projectile cannot start from the killing hit itself.

**Four aim-locked shells from a kneeling channel (league_jhin R, Curtain Call).** A `CasterAnimation` loops its tag
for its ticks, so the channel has three tags: `ult` (the deploy, 30 ticks), `ult_aim` (looped for the rest) and
`ult_shot` (12 ticks of recoil, then `ult_aim` again). One `AddCasted` poll on him (every 6 ticks for the 300 ticks
after the deploy) ends the channel when he is crowd-controlled (`RandomTarget` `AllyChampionInCC` at range 1) and,
when the gap flag `r_wait` is off, picks a champion damaged lately within 120000, else any in range: a hidden 8-tick
lob, then a `LinearProjectile` on `EnemyChampion` (20000 a tick). The count `r_s1` -> `r_s4` and the hit ladder
`r_h1` -> `r_h3` (+30% a shell that hit) are caster flags; the fourth deals twice the damage outright and ends the
channel when its shell is out. Flags, animations and sounds are queued on him (a `Delayed` on a target that died
runs only pictures).
Lifting the lines and bullets to the muzzles of the finished strips (W and R 9.5 and 8 px instead of 5) and firing W
3 ticks earlier, in its shot frame, raised the kill difference by about 0.2 each (+1.56 -> +2.0 over 1440 games).

**A bomb that sticks to the first unit where it lands (league_zilean Q, Time Bomb).** A `Targeting` cast on
`EnemyWithoutTower` (70000) lobs a `ParabolicProjectile` (24 ticks) at where the target stood when it left his
hand - a champion who keeps walking steps out of it. Its shape is a circle of 8000 on `EnemyWithoutTower`, and a
3-tick caster flag `q_lock` set by the first unit it reaches keeps the others out: entity order puts champions first,
so a champion inside wins over the minions round him (League's "prioritizes champions"). On that unit: the ticking
picture and sound in 30-tick pieces, each behind `SwitchByBuff q_off` (a picture once started cannot be stopped,
so a piece is the most that plays on after the bomb is gone), and a `Delayed` of 180 ticks - the fuse - that blows it
up round wherever the unit walked: a one-tick lob onto the unit's spot (league_annie R's) whose `end_effects` start
the blast (a one-tick `RangeProjectile`, radius 30000, magic damage to every enemy). Nobody near the landing: the
lob's `end_effects` find `q_lock` off a tick later, put the bomb's picture on the ground and blow it up there.
League's bomb also blows up when its carrier dies; queued on a dead unit the fuse's `Delayed` runs only its
pictures (section 4), so 8 of 27 bombs on minions were lost in a logged game. league_shaco R's watch finds the
death: on the carrier an `AddCasted` (`Fire`: a burn icon while it ticks, period 4) refreshes the 5-tick caster flag
`q_seen` and lobs a hidden watch at it; a `Delayed` of 6 ticks in the watch's `end_effects` (it waits at the landing
point) finds `q_seen` gone when the runs stopped with the carrier and, with `q_live` on (the bomb waits: set at the
stick, removed by the fuse's end and by the second bomb), sets `q_off` and blows the bomb up there - 2-6 ticks after
the death, a few pixels from the body (every carrier that died in two logged games).

**Hidden projectiles in flight move the AI (league_zilean Q's watch).** The watch lob copied from Shaco flew 6 ticks,
so with one every 4 ticks one or two were always in the air over the carrier. On Zilean that cost the kill difference
0.4 and 9% of his damage to champions in 720 games (seeds 25-48: +2.44 / 7276 without the watch, +2.01 / 6634 with
it), and the same lobs with their `end_effects` removed did the same (+1.97 / 6497): the lobs, not the blasts. On
`applied_target: AllyOnlySelf` they went the other way (+3.06 / 7545). A 1-tick lob whose `end_effects` wait in a
`Delayed` is in the air for one tick: +2.40 / 7424, the blasts it finds counted in. Keep hidden watch projectiles
short-lived. league_shaco R's watch (the same 6-tick lobs, but only while the clone lives: 300 ticks of a 50 s
cooldown) measured the same way in the jungle lane, three batches of 720 games: +1.08 / +1.27 / +0.90 with the 6-tick
lobs, +1.16 / +0.80 / +1.17 with the 1-tick lob, +1.02 / +1.23 with the lobs' `end_effects` removed - inside the
paired noise (about 0.30 a batch, the damage moving -1% to +6%). The AI does react to them: in 240 logged games each
the ult's target died during the clone 32.9% of the time with the 6-tick lobs and 39.8% with the 1-tick one (it walks
away from the lobs), while Shaco died first 3.2% against 5.1%; both blew up on every target that died under the clone
(379 and 470). Shaco has the 1-tick lob since 0.50.2 (the user's call, 2026-10-03): the target fights on as it would
in League.

**Rewind as the second bomb on the same champion (league_zilean W in Q, QWQ).** League's W resets Q, and the
players' combo is Q, W, Q: two bombs on one champion blow at once and stun everyone round him. The user picked it
automatic. Beside the bomb flies an invisible twin with the same path and shape on `EnemyChampion` (its own lock
`q_tlock`), so it finds only a champion near the landing; with W's 720-tick caster cooldown `w_cd` off it sets
`w_cd` and `q_pop` (the first bomb's blast is called off), poses him (`CasterAnimation w` 30 ticks, then Q's
`skill` again) and 42 ticks later throws the second bomb from a `Delayed` queued on that champion: a
`TargetProjectile` from the caster to him wherever he ran (`y_offset` -14000, the raised hand). Its hit sets
`q_off` (the first bomb's ticking stops), a 2-tick `skill_cooldown_mult` 60 with `ult_cooldown_mult` -60 (W's
"-10 s on his basic spells" as league_taric's burst: the cooldowns left are capped, the ult's untouched) and a tick
later the double blast round the champion: twice the damage and a 75-tick `Stun` on every enemy in it. In 720
simulated games: 18 Q casts on champions and 28 on minions and camps a game; in logged games about 11 double blasts
and 15-17 champion stuns a game.

**Slow one, haste another in one cast (league_zilean E, Time Warp).** League gives one or the other; the AI cannot
choose, so (the user's pick) a `Targeting` cast on `EnemyChampion` (70000) does both: the champion gets a 150-tick
`move_speed_mult` -35 buff, and an allied champion near Zilean +35 for as long - a `RandomTarget AllyNotSelf` at
40000, then (a 1-tick caster flag `e_got` says the first found nobody) at 80000; nobody: Zilean himself. The ally
next to him is hastened first, as a player would. 11.2 casts a game; 10 of 11 reached an ally.

**Experience as stats, handed over by a spell (league_zilean passive, Time in a Bottle).** No effect gives
experience, so the bottle gives what levels give: a caster timer `b_cd` (5400 ticks), started by each life's first
action (a `Permanent` caster flag `life` that death clears, section 5), fills it; the next E that hastens an allied
champion pours it out - that ally and Zilean each get a `Permanent` buff of +10 attack, +10 ability power and +80
health (same-name buffs add up, so every bottle adds an instance; death takes them away, as it clears every buff).
About 2.5 bottles a game.

**A revive as an undying rune, armed until someone is in danger (league_zilean R, Chronoshift).** League's rune
revives the ally who dies under it. Nothing reads current health or brings a unit back, but `undying: true` keeps a
unit alive while its buff lasts (also given to an ally by `AddBuff`): the rune is 300 ticks of `undying` on the
ally, and a tick before it ends the rewind - a heal of 400 + 150% ability power (`heal_type: Ally`) with its
picture. When: league_kayle R's armed ult - the slot (a 3-tick action on the `idle` tag, `EnemyChampion` within
60000) adds `r_armed` for 900 ticks, and every action checks: an allied champion in crowd control within 90000
first (`AllyChampionInCC`), else Zilean himself when two enemy champions stand within 40000 of him (Kayle's
two-flag count); a save plays Q's pose and the voice; an unused window caps the cooldown at 60 ticks. At 60000 /
30000 the check found someone 0.2 times a game, at 90000 / 40000 0.8. Nobody died under the rune; with a rewind of
250 + 80% 5 of 7 saved champions died within a second after it, with 400 + 150% (League's revive is 600-1100 +
200%) 3 of 6. A 60-tick stasis after it (`damaged_reduce` 100 + `cc_immune`, League's) was tested and left out.

**Two forms chosen in play (league_kayn passive, The Darkin Scythe).** A form is a `Permanent` caster buff
(`form_d` / `form_s`) that every slot reads with `SwitchByBuff`: the Darkin heals 20% of each champion hit's damage and
adds % max health, the Shadow Assassin adds true damage in a 180-tick window after combat starts; the forms' own cast
strips play through a `CasterAnimation` on the action's first tick (idle, run, hit and death cannot change - the engine
picks them). The charges are `Permanent` step flags (`dc1`, `sc1` ...) climbed by spell hits on champions - near ones
for the Darkin, W's hits on far ones only for the Shadow - and the top step removes them and adds the form, its
aura (a `view_buffs` picture), the transform sound and, 2 ticks later, the transform pose. Data cannot read the
target's attack range, and death clears every data buff, so the main pack's thresholds are low (2 / 1: 81% of lives
form, median 33 s); the optional native add-on `addons/league_kayn_form` swaps the charge blocks (wrapped in a no-op
marker `RemoveCasterBuff league_kayn_mk_charge`) for tags it counts by the champion's range and keeps the form on
respawn (native decides, data shows - section 9).
On game 0.6.2 the add-on also changes the whole body (v0.2, `src/view.rs`): the game builds a unit's sprite path from
the name in its view data every frame (`asset/base/aseprite_resources/champions/{name}`, then the asset remap table), so
a hook on that builder finds Kayn's view record and the client extension rewrites the name's last letter
(`league_kayd` / `league_kays`). `mod.override_info` sends those names to whole form sheets (idle, run, hit and dead
included), built by `tools/art/import_native.py`. Two lessons for any native view change:
- The client's match view sim (`ClientMatchView`) is not the screen. It simulates the whole match in seconds, and the
  screen replays it later. Kayn's 7:38 transform was drawn while the screen showed level 2. Record each change's tick
  in the view sim, and apply it when the screen's match clock reaches that tick. The clock is the UI label
  `ingame.header.game_time.value`; UI paths are dot-joined node ids.
- `ingame.header.dm_scoreboard.timer` is the deathmatch clock: hidden in MOBA and stuck at `02:00`. Check that every
  node on a UI path is visible before trusting its text.

**Riding inside a champion (league_kayn R, Umbral Trespass).** A `Targeting` cast on `EnemyChampionRecentlyAttacked`
(the team's recent target) dives with `MoveToTarget`; its `end_effects` hide him for 120 ticks (`CasterInvisible`, a
caster flag with `damaged_reduce` 100 and `cc_immune`, and a `CasterAnimation` on an empty tag `r_hidden`), mark the
target, and re-dash onto it every 10 ticks (`Delayed` `MoveToTarget`s) so he moves with it; the last one's
`end_effects` burst out with the damage and the form's extras.

**A blade that bounces on her attacks for a few seconds (league_sivir W, Ricochet, folded into the attack).** Every
600 ticks (300 while R hunts) the next attack sets `w_on` (240 ticks, +45% attack speed). An attack under it throws
the homing `w_blade` and, at the same speed and height, Miss Fortune Q's wide penetrating twin (`w_twin`: radius
20000, reach the attack's range + 50000): the units the twin touches in a 9-tick window after the blade hits take one
bounce each - a ladder of flags (`w_h1`, `w_h2`; the third bounce shuts the window), 60% attack damage as an `Attack`
(so it can crit) 5 ticks after the hop's picture. A 1-tick `w_wait` flag set by the blade's own hit keeps the twin
from bouncing onto the unit the blade just hit.

**A boomerang that flies out and back, the hand empty until it returns (league_sivir Q, Boomerang Blade).** A
`Direction` cast on `EnemyWithoutTower`; 8 ticks before the throw a champion within range + 20000 is aimed at
(league_caitlyn Q's hidden lob: its `end_effects` throw the blade at the spot he stood on, so he can step out),
else the blade flies the cast's way to its full reach (waves, camps). The blade is a penetrating `LinearProjectile`
(6500 a tick, 110000, 60 + 80% on everyone it passes) whose `end_effects` start a `BackToCasterLinearProjectile`
(7000 a tick) with the same hit; that one's `end_effects` remove the `skill_wait` caster animation (the empty-handed
hold started on the throw tick, `q_hold` 60 ticks) and play `skill_catch`. `BackToCasterLinearProjectile` takes no
`y_offset` (it flies at the pivot's height): the outbound blade stays near it as well (-2000), or the picture jumps
at the turn.

**A spell shield that pays out when the first hit lands (league_sivir E, Spell Shield).** Nothing reports "a spell
was blocked", but a shield breaking can be seen: E puts a 1-point `Shield` on her (`tick` e_cap + 4), a caster flag
with `WithShield` as its duration (`e_guard`: it lasts while the shield does), `skill_damaged_reduce` 100 +
`cc_immune` for e_cap (180) ticks, and a 2-tick lob starts a `RangePeriodProjectile` on `AllyChampion` (period 6)
that checks on her: the window flag (`e_guard_on`) still on but `e_guard` gone = the shield broke -> the heal (60 +
40% attack), Fleet of Foot, the picture, and the shroud removed `e_grace` (60) ticks later (a second spell landing
with the first is still blocked). Any hit breaks the point, not only a spell. The AI casts it on `EnemyChampion`
within 65000; it paid out about 4 times a game (a fixed 90-tick window like league_nocturne's W paid about once).

**Cooldown cuts on champion hits while hunting (league_sivir R, On The Hunt).** League's R takes time off her basic
spells on every champion hit. A 2-tick caster flag with `skill_cooldown_mult` m (and `ult_cooldown_mult` -m, so the
ult keeps its cap) caps each remaining cooldown at cooltime x 100 / (100 + m) (league_taric's way); a ladder of
300-tick flags (`r_c1`, `r_c2`) gives the 1st, 2nd and 3rd hit 25, 60 and 110, and any spell cast resets it.
Ricochet's own cooldown halves while she hunts. A champion killed by her blade renews the hunt (league_jinx's kill
check: a flag on the champion that her `casted` clears the next tick while he lives; a corpse lob reads it).

**A real card cycle over his head, locked when the wanted card comes up (league_twistedfate W, Pick a Card).**
The cast (`EnemyWithoutTower`, so waves and camps get cards too) sets `w_shuffle` (360 ticks) and starts an
`AddCasted` poll every `w_step` (30) ticks that steps the current card - a `w_cur_<card>` flag and its picture over
his head (`w_show_<card>`, a `view_buffs` entry) with the flip sound. The AI's wish is read at each step: an enemy
champion within `w_reach` -> gold; two or more units within `w_group_r` of the target (a count ladder `w_g1`,
`w_g2` made by a `RangeEffect`) -> red; else blue. When the current card is the wished one it locks: the shuffle
flags go, `w_<card>` (360 ticks) and its blazing picture go on, the lock voice plays. The next attack's throw reads
`w_<card>` with `SwitchByBuff` and throws that card's homing projectile instead of the plain one; the gold card only
leaves for an enemy champion within the attack's range + `g_reach` (with none, a plain card flies and gold stays
locked). Blue's hit puts a 2-tick `skill_cooldown_mult` flag on him (his cooldowns cut, the refund), red's a
1-tick lob whose zone hurts and slows round the target, gold's a `Stun` with a `ViewEffect` of turning stars for the
stun's length (every CC needs a mark on the target: the user missed it). Stacked Deck counts every throw (a
`Permanent` ladder `e1`..`e3`; the fourth adds magic damage and the hand flash).

**Dice on kills (league_twistedfate passive, Loaded Dice).** League's gold cannot be given from data, so a kill
rolls a small ability power bonus until death. league_jinx's kill check finds the kill (a Q hit reads its own flag
k_read ticks later; an attack reads once after the card's longest flight); a `Permanent` ladder `d1`..`d5` walks a
fixed scrambled order of faces (`dice_seq` 4, 1, 6, 3, 5, 2), the face shows as a `ThreePhase` view (pre
`dice_roll`, loop `dice_k`, remove `dice_out`) on a 54-tick flag, and its ability power (`dice_ap` 0, 0, 1, 1, 1,
2) is added to a `Permanent` caster buff. Death clears every data buff, so the bonus goes with him (League's
gold would stay; an add-on could pay real gold through `player_add_gold`).

**A Gate to a fight far away (league_twistedfate R, Destiny / Gate).** No data or native call changes vision, so
Destiny is a picture: a `RangeEffect` (2000000) puts `r_seen` (360 ticks) with its eye on every enemy champion.
The Gate is league_ryze R's armed poll: a 3-tick `idle` action on `EnemyChampion` (range 960000) arms an
`AddCasted` poll that waits while any enemy is within `r_near`, then picks `EnemyChampionRecentlyAttacked` (his
team's fight) 70000-360000 away and sends a probe `TargetProjectile`; an ally within `r_mate` of that champion
(`from_projectile`) confirms the fight. Then: the marks, `ult` with `r_cast`, `ult_gate` with `r_gate` for the
90-tick channel (CC checks every 15 ticks break it: no teleport, no gold card), a beacon `LinearProjectile`
stopping `r_stop` (25000) short of the target with the destination mark on the ground, a delayed `Teleport` there,
`ult_land` with `r_in` and the gold card locked. Landing 5000 away cost 0.9 deaths a game in the simulation;
25000 short and a 90 s cooldown kept the help without the dives.

**A shade after a quiet spell (league_evelynn passive, Demon Shade).** Every action but W starts with `act`: it
refreshes a caster flag `fight` for `idle` (240) ticks, takes the shade off (`shade`, `sh_regen`) and queues a
`Delayed` of the same length on her (in a self-only `RangeEffect`, so a projectile's hit can queue it too) that enters
the shade unless `fight` or `shade` is on - only the last action's check finds `fight` gone. Entering: `shade` for the
poll chain's length, E's cooldown flag off and the empowered whip armed (`e_emp` with a `range` caster buff `e_range`,
so the AI opens with the dash from farther), the sound, and an `AddCasted` poll (every `poll` 10 ticks for `poll_len`
600, chained `poll_levels` 3 times by a delayed self `RangeEffect` while she stays in it) that renews `sh_regen` (an
`hp_regen` buff of `regen` 12: the data reads no current health, so it heals at any health instead of League's
below-a-threshold regeneration) and, once `lvl` is on, `CasterInvisible` for poll + 4 ticks, so the camouflage lapses
within a poll after she acts. W does not call `act`: casting it keeps the shade, as in League.

**A level gate read twice (league_evelynn's camouflage from level 5).** The data reads no level past
`SwitchByLevel3`, so entering the shade runs league_kayle's probe (a 3-tick shield halfway between her level-4 and
level-5 health against her own hit of 10% of her maximum health, a 2-tick `undying` guarding the rest; then a 99 hit
held by a 100 shield, so no damage amplification fakes a level). One pass was fooled at level 4 by a monster's hit
landing in its 2-tick window; now a second pass `probe_gap` (30) ticks later, run only while she is still in the
shade, has to agree before `lvl` goes on (`Permanent`, until she dies). A `WithShield` flag that holds 2 ticks before
her own shield means somebody else's shield is on her: the probe waits for the next shade. In the simulation the gate
opened after level 5 in every seed.

**An ult that waits for her combo (league_evelynn R, Last Caress).** League's R comes after her hits (it deals 2.4x
to champions below 30% health). The AI casts an ult slot as soon as it meets a champion (and never cast an
`AllyOnlySelf` slot at all), so the slot - a 3-tick `idle` action on `EnemyChampion` (`r_slot_range` 60000) - only arms
`r_armed` for `r_arm` (600) ticks, refunding its cooldown (a 3-tick `ult_cooldown_mult` 4900 flag) when the window
lapses unused. Her attacks fire it: while armed, an attack that is not the empowered whip (`r_skip`: the dash and the R
pose would clash) checks her recent champion hits - a ladder `h1`..`h4` climbed by a champion-only twin of every
attack and lasher hit and by every spike sent at a champion, started over after `h_win` (240) ticks without one - and
fires at an enemy champion within `r_reach` once the ladder reached `r_need` (3), or `r_need_d` (2) with two enemy
champions within `r_crowd`. Fire: `ult`, untargetable for the cast (`CasterInvisible`, `damaged_reduce` 100,
`cc_immune`), a `DirDot` cone (radius 45000, `range` 342 = 140 degrees, `Forward` 1000) of 150 + 75% AP plus 35% per
rung (x2.4 at the top: counted from her own hits, the target's health being unreadable), a `MoveBack` (9000 x 5 ticks)
away from the champion picked, and the shade 75 ticks later (`act(idle=r_shade)`: League's 1.25 s). The slash's picture
is a view-only `LinearProjectile` that crawls 30 ticks toward that champion (a slow homing shot would stay in the match).

**Damage taken as a resource (league_sett W's Grit; in the SDK simulation the levels climb in fights, 2026-10-05).**
League's Grit stores the damage Sett takes. No effect hears damage, but league_sivir E's hit sensor does: a 1-point
`Shield` (`tick` 36000) on him through a self-only `RangeEffect`, then a caster flag with `WithShield` as its duration
(`grit_sense`), gone 2 ticks after a hit breaks the point (section 5). His attack and ult start with the check: no
`grit_init` (`Permanent`, cleared by death) -> arm the sensor and set it; `grit_sense` gone -> he was hit since the last
check: one more Grit level and arm again. The levels `grit_1`..`grit_5` are exclusive 240-tick flags, each step
removing the one before it (league_kaisa's Plasma), the top one refreshed, so Grit is gone 4 s after the last hit
counted. W reads the level from the top and spends it on a self-only `Shield` and on the true damage of the punch's
middle line, one branch per level. What it counts is "hit since his last attack", not how much: a level per check
window. Any other shield on him (W's own, an ally's) keeps `grit_sense` alive, so no Grit is counted while one holds.
The check stays out of `skill` / `skill2` (copied every tick, section 8). `tools/kit/sett_kit.py` writes it;
`GRIT_MAX = 0` drops it for a fixed shield.

**Stun only when two or more are pulled in (league_sett E, Facebreaker).** League stuns when enemies stand on both
sides of Sett. No shape tells front from back (`Forward` is unsigned, a circle round the caster has no sides), so the
pull is a circle (`Grab` without `tick`, they stop at him) and "both sides" becomes "two or more": a first
`RangeEffect` on the same circle climbs 1-tick caster flags (`e_one` -> `e_two`, league_blitzcrank's count), and a
`SwitchByBuff e_two` in the same tick picks the circle with `Stun` or the one with the slow. A native add-on could
check the sides (league_camille_wall's way); the data pack keeps the count.

**Throw a champion forward and land on it (league_sett R, The Show Stopper).** `Targeting` on
`EnemyChampion`: `Stun` on the target from the cast to just after the latest slam and a `cc_immune` caster buff; at
the throw tick `Knockback {speed 3000, tick 8}` on the target (24000 away from him) and, in the same `Delayed`,
`MoveToTarget` at the same speed. It homes on the target (league_leesin's QRQ chase), the gap stays while the target
flies and closes once it has landed, so he always lands on a target that has stopped, whatever the cast distance;
the slam runs from the dash's `end_effects` (league_malphite R): `ult_slam`, then the crater, a `RangeEffect` round
him and the thrown champion's own extra share of its maximum health (League scales the slam with the thrown
champion's bonus health; nothing reads another unit's health).

**Combos from the first skill's flag (league_sett R -> E, E -> W, R -> W; 2026-10-05).** As league_leesin's, the slot
cast second plays the combo from a caster flag the first one left, and no slot is held: the slam adds `r_combo` and
`w_combo` (150 ticks), a Facebreaker stun adds `w_combo` (90) only through a `RangeEffect` on `EnemyChampion` round
him (a stunned wave does not count). Facebreaker in `r_combo` takes the stun branch whatever the count; Haymaker in
`w_combo` lays its true-damage line as wide as the fist. Each branch removes its flag. Few combos fire by
themselves (in 10 simulated minutes about one R -> E and two W in `w_combo`); casting Facebreaker on
`EnemyChampion` instead of `EnemyWithoutTower` mattered more (9 casts, 7 on champions, against 28 and 3.5), and
together they took him from +0.45 to +0.79 kills a game over two batches (porting-heroes "Balance check").

**A thrall where the champion she killed fell (league_lissandra passive, Iceborn Subjugation).** League raises any enemy
champion that dies near her; nothing reports a death and a `Delayed` queued on a dying unit runs only its pictures, so
the spot is taken in the same tick as the damage: every damaging source (the attack's champion-only twin, Q's twin line,
W's ring on `EnemyChampion`, R's target) adds league_jinx's kill flag `k_<src>` before the damage and a 3-tick
`AddCasted` that clears it after (a living target clears it, a dead one never runs it), and fires a hidden 1-tick
`ParabolicProjectile` at the target - fired straight from the effect list (a RangeEffect's per-target list or a
`RandomTarget`), never from a projectile's `applied_effects`, where projectiles do not spawn. Its `end_effects` wait
`flight + 3` ticks at the landing spot and, with the flag still on, raise the thrall there (a `ViewEffect`) and shatter
it 90 ticks later (a `RangeProjectile` burst + slow). The wait must outlast the projectile: read on the tick the bolt
hit, the flag had not been cleared yet and a thrall rose over a living champion (the attack's longest flight is range +
40000 at its speed). In three logged games all 8 thralls stood on real champion deaths.

**Ring now, else glide in on the claw and ring (league_lissandra W with E folded in).** A `None` cast on `EnemyWithoutTower`
(85000): an enemy unit within the ring's radius rings at once; else, with E off its own cooldown flag (`e_cd`, 15 s), an
`EnemyChampionRecentlyAttacked` within reach gets the claw (a penetrating damage line) and a hidden non-penetrating line on
`EnemyChampion` with the claw's speed and a radius of the stop distance, whose `end_effects` `Teleport` her and ring 4 ticks
later (a `RangeEffect` round the caster runs where she landed); else the claw alone flies at a champion or any enemy in
reach - a poke that clears waves without blinking into them, and never an empty cast. 3-7 blinks a game.

**One ult, two tombs (league_lissandra R, Frozen Tomb).** League freezes an enemy or, low on health, herself; health is
unreadable, so crowding stands in (league_kayle R): the slot only arms the ult (a 3-tick `None` cast, refunded after 600
ticks unused) and her attack, Q and W check it: two enemy champions within 30000 (the n1/n2 ladder) -> herself: 150 ticks
of `CasterAnimation ult_self`, a `damaged_reduce` 100 + `cc_immune` caster buff (it carries the ice block's picture) and a
heal over the stasis; else an `EnemyChampionRecentlyAttacked` within 60000 -> a stun, the tomb buff's picture and the
damage. Either way a 1-tick lob onto the tomb starts the burst and a `RangePeriodProjectile` field (180 ticks, a 20-tick
slow every 15) - zones need a point, the lob gives one even on herself.

**A smart charge (league_varus Q, Piercing Arrow).** League holds the bow up to 1.25 s; the AI can't hold a key, so the
cast picks the draw: a `Direction` cast on `EnemyWithoutTower`, and an enemy champion within 130000 at the cast -> the full
draw (`CasterAnimation skill`, 66 ticks), else the quick one (`skill_quick`, 24 ticks, 60% damage, a shorter arrow). The
action itself lasts 3 ticks and the animation holds him (league_aatrox Q). The arrow is aimed at the release, at where a
champion in reach stands then (dodgeable), else along the cast; it pierces, and the falloff (100 / 80 / 60%) counts on
caster flags for this arrow - three steps, since each step doubles the branch (four steps put the Q tree at 332 nodes).

**Stacks counted on the caster, burst on the target (league_varus Blight).** Nothing reads a buff count on the target, so
his attack's champion-only twin climbs a caster-flag ladder b_1 -> b_2 -> b_3 (league_kaisa's Plasma; 360 ticks, refreshed
by every hit) and shows the pips on the target. Q, E and R hits on a champion read the ladder: 3% of the target's maximum
health per stack as true damage (`FixedAttack` `target_hp_ratio`; nothing magic reads max health) and, for Q and E, a
2-tick `skill_cooldown_mult` 15 / 35 / 64, which caps every cooldown at 87 / 74 / 61% (League's 13% refund per stack;
the cap reaches R too, a small bonus); then the ladder clears. The count is his, not the target's - switching targets keeps it, a rare and harmless gap. W's active
(Blighted Arrow) folds into the full draw: with its own 40 s flag gone it adds 6% max health on the champion detonated.

**A hail on a point, then ground that slows and cuts healing (league_varus E).** A `Position` cast on `EnemyWithoutTower`;
the arrows land 20 ticks after the release on the cast point (dodgeable), then a `RangePeriodProjectile` field for 240
ticks re-applies a 15-tick slow (30%) and `heal_reduce` 40 every 15 ticks, so it never stacks up.

**A chain that roots and spreads (league_varus R).** A `Targeting` cast on `EnemyChampion`; at the release a tendril line
(passes minions, stops on the first enemy champion) roots 120 ticks, detonates the stacks (no refund) and sets three; its
`end_effects` drop a delayed zone at the hit spot: 30 ticks later every enemy champion within 55000 is rooted 90 ticks and
shows three pips (the pictures only - the ladder is his, set once).
**Crit stacks that drain one at a time (league_tryndamere Battle Fury).** Five caster flags f_1..f_5, each `crit_chance` +8
(the engine's crit: 2x, on the basic attack only); his attack climbs one, every unit E passes one, a killing blow two
(league_jinx's kill check). All of f_1..f_n are on at once and only the top one ticks (f_top 300); every lower one lasts
f_step 60 more (league_jax Relentless Assault), so Fury holds 5 s after the last hit, then drains a stack a second. Only
f_5 has a view (the full-Fury glow) - five stacked pictures would draw five auras.

**An armed save that can't die (league_tryndamere R, Undying Rage).** Health is unreadable, so the R slot only arms
(league_kayle R: a 3-tick cast on the idle tag adds r_armed for 900 ticks, refunded through `ult_cooldown_mult` when
unused) and his attack checks the danger: two enemy champions within 30000, or hit at five checks in a row (league_sett's
1-point shield as the hit sensor, one level of h_1..h_5 a check). A save: full Fury, an `undying` caster buff for 300
ticks (health stops at 1), and at tick 290 Bloodlust heals by the Fury held and spends it. One-tick `chk` / `go` flags keep
the check written once in the attack tree (duplicated it was 745 nodes; now 286). The danger proxy fired at a median 75%
health in the SDK - the optional native add-on addons/league_tryndamere_rage (a `StablePassive` reading health in
`on_update` / `on_damaged`) fires it below 15% instead; the main pack stays complete without it.

**A shout that slows only the ones leaving (league_tryndamere W, Mocking Shout).** Nothing reads facing; League slows
enemies turned away, i.e. running off, so the far ones stand in: every enemy champion within w_r loses 25% attack, and
those beyond w_near (12000) are also slowed 40% - two `RangeEffect`s, the near one adding a +40 buff that cancels the slow.

**A wait that kills shorten (league_xerath Mana Surge).** Nothing subtracts time from a buff, so the passive's 14 s wait
is four caster flags laid at once (p_a..p_d: 210, 420, 630, 840 ticks); he is ready when none is left (four nested
`SwitchByBuff`). A unit his orb or Shocking Orb kills (league_jinx's kill check) removes the LONGEST flag still on: the
remaining ones expire 210 ticks apart, so each kill brings the surge exactly 3.5 s closer (League's refund) with no poll.
The surge orb's hit adds a 2-tick `skill_cooldown_mult` 30 / `ult_cooldown_mult` -30: the mana League refills becomes
cooldown here.

**A stun that grows with the distance flown (league_xerath E, Shocking Orb).** No effect knows how far a projectile went,
but its speed is fixed: two caster flags laid at the release (e_d1 for e_band1 ticks, e_d2 for e_band2) tell the hit how
long the orb flew - e_d1 still on: the short stun, e_d2: the middle one, neither: the long one (0.75 / 1.33 / 2 s).

**A follow-up that lands where the first skillshot found a champion (league_xerath E -> W).** The orb stops on the first
enemy (minions too); a champion-only twin on the same line passes the minions, and its hit sets a flag and, a tick later,
lobs the Eye (a 1-tick `ParabolicProjectile`) onto that champion - stunned already when the orb reached him too. With
no champion on the line, a `Delayed` of e_fall ticks on the cast target (it reads the flag) lobs the Eye there instead.
The Eye's two zones (the ring and the sweet spot) share one centre: the centre's extra damage and slow are a second,
smaller `RangeProjectile` with the same timing.

**Long-range shells from a standing channel (league_xerath R, Rite of the Arcane).** league_jhin R's channel: the
deploy tag, then a looped channel tag; one `AddCasted` poll on him every 6 ticks ends it on crowd control and, between
shots (a r_wait flag), picks a champion his team is hitting within 220000 (else any): a 1-tick lob marks the spot (its
`end_effects` play the warning ring and, 8 ticks before the blast, the falling bolt as `ViewEffect`s - upright, never
turned) and the blast zone hits r_delay ticks later. A champion-only twin zone on the same spot sets a 2-tick flag the
`Delayed` read after the blast climbs into the ramp ladder r_h1..r_h3 (+20% a rung for the later shells); r_s1..r_s3
count the shells and the fourth ends the channel.

**Knock back everyone but the one you challenge (league_xinzhao R, Crescent Guard).** A `Targeting` cast on
`EnemyChampion`; on the sweep's tick (a `Delayed` of the cast) the cast target first gets a 3-tick `AddBuff` with
`cc_immune: true`, then a `RangeEffect` round the caster damages and `Knockback`s every enemy in it - the challenged one
is immune for that tick and stays beside him *(SDK simulation, 2026-10-06: the knock-backs are `ForceMove` events 15-16
ticks after the cast; in 14 casts over three games the target never had one then, the minions and champions round him
did)*. The same 3 ticks also shrug off any other crowd control that lands on that tick - too short to matter.

**A dash that arms the next three attacks (league_xinzhao E -> Q, Audacious Charge and Three Talon Strike).** The E
lands (`MoveToTarget`'s `end_effects`) and adds `q_1` (240 ticks); the attack picks on tick 1, `q_1` -> `q_2` -> `q_3`
-> none, each with its own strip (`CasterAnimation q1/q2/q3`) and its hit in a `Delayed`, the third adding `Airborne`
45; Determination's third-attack count (two 240-tick counters, league_diana's) runs alongside, so every branch is
built twice (passive or not): 12 leaves in one `SwitchByBuff` tree. Each of `q_1`..`q_3` binds its own picture (3, 2
and 1 gold talon marks over his head), so the count shows.

**A gun at range, a sword up close, picked per attack (league_samira).** The attack's effect fires on tick 1: a hidden
`TargetProjectile` (speed 100000) at the target whose hit runs `RandomTarget AllyOnlySelf` within pm_reach (league_morgana's
reach check) and sets a 4-tick caster flag a_close - set only when she stands that near; a second probe on
`EnemyChampionInCC` sets a_cc. Two ticks later a `SwitchByBuff` tree picks the juggle (a_cc, its own 360-tick cooldown
flag), the sword (a_close: `CasterAnimation attack_m`, the cut in a `Delayed`) or the gun (the action's own `attack`
strip, the bullet in a `Delayed`). The gun's strip shows for the 3 ticks before a sword strip takes over - too short to
see.

**A grade that climbs on different kinds of hit (league_samira's Style).** Six permanent caster flags g1..g6 (one at a
time, each with its move speed), a g_live timer run again by every champion hit, and per kind a short hit flag c_<kind>
and a last-kind flag l_<kind>. Each action reads its own c_<kind> once, after its hits: a kind other than the last one
climbs a grade (the ladder `SwitchByBuff g6 / g5 / ...` written once), the same kind only keeps it. The first read after
g_live ran out drops the grade - nothing else runs on a timer. Each grade binds its own picture (the letters E..S over
her head, never mirrored).

**An ult only at full grade (league_samira R).** The AI casts an ult slot whenever a champion is in reach, so an empty
branch below S would waste the cooldown: the slot only arms r_armed for 330 ticks (refunded through a 3-tick
`ult_cooldown_mult` when it lapses, league_evelynn R), and at S - or the next attack at S while armed - it fires: the
grades and the last kinds go, a 120-tick `CasterAnimation`, life steal, and the shots on her own `AddCasted` so crowd
control stops the spin but not the shots.

**An execute without reading health (league_pyke R, Death from Below).** League executes champions under a threshold
T and deals T/2 to the rest; nothing in the data reads current health. The X's zone deals T as `FixedAttack` (true
damage) to every enemy champion in it - those under T die - and a `Delayed {tick: 1}` in the same `applied_effects`
(queued on the champion hit) adds `Heal {amount: T/2, attack_ratio: half of T's, heal_type: "Any"}`: a survivor is
healed back half, so it loses T/2 as in League, and a dead unit is not revived *(measured in the SDK simulation with an
HP trace, 2026-10-06: 377 dealt then 188 healed; the executed stayed dead)*. A heal reduction on the target makes the
survivor lose a little more. The kill check (league_jinx) on the same champions blinks him onto the dead (a `Delayed`
`Teleport` on the target, read while the kill flag still holds) and takes the ult's cooldown off for a recast. A shared
kill flag means a survivor in the same X hides another's death; the exact execute is a native add-on's job.

**A phantom that comes back (league_pyke E, Phantom Undertow).** Where the dash starts, league_ekko's anchor (a
`LinearProjectile` of speed 1 and range 1) ends at once; its `end_effects` hold that spot, and a `Delayed` there throws
a penetrating `BackToCasterLinearProjectile` from it back to him, stunning every champion on its way. At 40 ticks it
hit 3 of 37 casts (he had walked off by then); thrown 12 ticks after the dash at 12000 a tick, 25 of 32.

**Grey health (league_pyke passive, Gift of the Drowned Ones).** League stores champion damage and heals it back while
he is unseen. league_sett's hit sensor (a 1-point `Shield` and a `WithShield` caster flag) is read by his attack and
his ult: broken -> one more grey level (g1..g5, each 480 ticks) and a `hurt` flag for 180 ticks, the sensor armed again.
The levels heal back in W's camouflage, and each attack also queues a 180-tick `Delayed` on him that heals them if the
sensor is still whole and `hurt` is gone - nobody hit him for 3 s. What it counts is "hit since the last check", not how
much.

**A mist that hides her from outside (league_gwen W, Hallowed Mist).** Where E lands, league_akali's first shroud: Ekko's anchor (a 1-range `LinearProjectile`) whose `end_effects` start a `RangePeriodProjectile` on `AllyChampion`, every 6 ticks a `RandomTarget AllyOnlySelf` from the zone refreshing `CasterInvisible` (8 ticks) and armour / MR. Enemies far away lose her; the ones that walk up still pick her (League: untargetable from outside). Leaving the mist ends both within 8 ticks.

**An ult woven with attacks (league_gwen R).** League recasts Needlework three times with attacks between. One cast throws the three volleys as `Delayed` `LineRangeProjectile`s 36 ticks apart, but the action holds her only for the first throw (r_t0 + the pose): the later volleys fly from where she stands in the cast's direction while the AI attacks. Only the first carries a `CasterAnimation` (a later one would cut her attack pose).

**A stack counter drawn by one buff per slot (league_gwen Q stacks).** qs1..qsk are all on at k stacks; each buff's view is one mark in its own slot over her head, so k marks show without any counting logic.

**Stacks that blow up the third time, counted on him (league_brand passive, Blaze).** Every spell hit sets the unit ablaze: two `AddCasted Fire` instances (magic every 60 ticks for 240; one per hit, as League re-applies Blaze). Nothing reads a buff count on the target, so the stacks are league_kennen's caster ladder b_1 -> b_2 (240 ticks), climbed a tick later from a champion-only hit (a zone on `EnemyChampion`, or `RandomTarget {range: 1, EnemyChampion, from_projectile}` in a non-penetrating line's hit) behind a 3-tick lock per spell; a champion hit while b_2 holds adds an `unstable` buff (its picture) and `Delayed 120` a 1-tick lob onto him whose zone is the blast (magic + `FixedAttack target_hp_ratio`), and the ladder clears. The ladder also stands in for "the target is ablaze" (W's +25%, E's wider spread). The burn's own % max-health true damage (on every R bounce too) made the draft +5.62: dropped. The native add-on addons/league_brand counts per enemy: build_brand native=1 puts a `Native` league_brand:blaze where the climb was; it stacks a buff named for the Brand on the champion (`entity_stack_buff`, max 3, refresh), at 3 clears it, lays a per-Brand lock and the `unstable` picture buff, and `queue_effect`s its own blast (magic with the % max health, its burn ticks queued too); every stack refreshes b_1 on him, so W and E read it as before.

**A bouncing ult without a projectile from the target (league_brand R, Pyroclasm).** Every projectile leaves from the caster (league_nami W), so after the seed's hit a 1-tick lob onto the target opens a chain of lobs on that spot (`travel_time` r_gap each, nested once per bounce - one level each, never a branch per level: two branches per bounce made 2^5 copies); each landing picks the next unit round the first spot with `RandomTarget from_projectile` - `EnemyChampion` first; after a champion hit (flag r_pc) only when a champion count zone found two (r_n2), else `EnemyWithoutTower` - and plays a seed falling on it, the hit r_fall ticks later. The cast is gated: a lob onto the target counts the enemies round it (u_1 -> u_2 flags); alone, the cast is called off and `Delayed 6` a 3-tick `ult_cooldown_mult` 4900 brings R back in 60 ticks (laid during the 6-tick action it did nothing: the cooldown starts when the action ends).

**A combo into the other slot (league_brand E -> Q -> W).** skill2 (E then Q, on `EnemyChampion`) sets `q_champ` when Q's fireball hits a champion; q_rel + 6 ticks later, with W's shared cooldown flag w_cd off (the W slot's effect is an empty branch while it runs: league_leblanc W), it casts W's pillar on the `EnemyChampionInCC` in reach - the stunned one - and lays w_cd: three hits, the third stack.

**One skill that starts another (league_alistar E -> Q).** League's Trample is folded into Pulverize and into
Headbutt -> Pulverize: with its own cooldown flag off, a cast also starts the trample - one `AddCasted` on himself
(`RangeEffect AllyOnlySelf`) that stomps every 30 ticks for 3 s on `EnemyWithoutTower` round him, its first stomp on
the wind-up. Every stomp that touches a champion climbs a caster-flag ladder e1..e4, and each champion the slam throws
up counts one too (League's E Q: the stomps land on them in the air); the fifth arms e_ready, and his next attack's
champion-only twin stuns 60 ticks and clears it.

**A dash that ends in a slam where the push left them (league_alistar W -> Q).** A `Targeting` cast on `EnemyChampion`:
`MoveToTarget` (3500 a tick) with `end_effects` = the headbutt (damage + `Knockback` 2500 x 8 ticks on the champions in
front) and a `Delayed` 6-tick slam ring round where he stands - the same Pulverize ring, so it lands on the champion
just as the knock-back sets him down.

**Crowd control counted for a passive (league_alistar Triumphant Roar).** Every crowd-control effect's champion twin
(the knock-ups, the headbutt, the stun) climbs a p1 -> p2 ladder on the caster; the third, with the 300-tick cooldown
flag off, heals him and every allied champion within 40000 (`RangeEffect` `AllyChampion`) and clears the ladder.

**An unstoppable roar fired on contact (league_alistar R).** Armed like league_blitzcrank R: a 3-tick `None` cast on
`EnemyChampion` arms the slot 600 ticks; every action and a 15-tick pulse fire it when an enemy champion is within
32000 or he is crowd-controlled himself: `cc_immune` 60 ticks (League's cleanse), `damaged_reduce` 50 for 420 ticks,
the aura drawn behind him (view_buff `z` -1). Unused, `ult_cooldown_mult` refunds the cooldown.

**Isolated: nobody of the target's side beside it (league_khazix Q, Taste Their Fear).** League's Isolated is "no allied
unit within 375 of the target". A `RangeEffect` is centred on the caster, so the count is taken at the target: on tick 1
of the `Targeting` cast a hidden 1-tick `ParabolicProjectile` lands on the target's spot and its `end_effects` start a
`RangeProjectile` (`delay` 1, `apply` 1, radius 30000, `EnemyWithoutTower`) whose applied effects climb 1-tick-renewed
caster flags `i1` -> `i2` (league_kayle R's count; the target itself is the first). The claw lands on tick 12 (well after
the count) and reads them: `i2` -> the plain hit, `i1` alone -> the isolated one, neither -> the plain one. In the
simulation (6 logged games, the draft numbers) 49 of his 81 Qs on champions (60%) and 224 of 302 on camps (74%) came
out isolated (a camp's monsters stand apart).

**Evolutions read from a level, ability power as the gauge (league_khazix).** League's evolution points come at levels
6, 11 and 16; here Q, E and R evolve at 5, 8 and 11 from league_kayle's probe, with two lessons. (1) Inside an attack
action the probe's self-hit rolled critical strikes (`attack_type: BaseAttack` crits every `FixedAttack` too, section 4)
and broke the shield at twice the measured size once he bought crit chance: the hits now come from a 1-run `AddCasted`
on him (damage over time never crits). (2) Maximum health is no gauge for a hero that buys health: 0 to 800 item health
at level 8 in 16 simulated games put E's and R's evolutions up to three levels early. He gains 1 ability power a level
instead (`growth.magic_power` 1; nothing in his kit reads AP and no item he buys gives any): under 2 ticks of
`damaged_reduce` 99 and `magic_resistance_penetration` 100 an `ApAttack` of 1000000% AP (100 x AP after the cut) hits a
3-tick shield of 100 x (level - 1.5) plus a 1-tick soak shield; another shield already on him skips the probe, a 100
shield against a 9900 hit guards against damage amplification, and two passes 30 ticks apart must agree. Each life's
first attack re-reads the stages silently. In the simulation every stage came 1-5 s after its level.

**Recasts as cooldown caps (league_khazix R, Void Assault).** League's R can be cast again within 12 s. The slot's real
cooldown starts at each cast; a first cast (flag `r_c1`) and, evolved, a second (`r_c2`) add a 3-tick
`ult_cooldown_mult` that caps it at 120 ticks, so the AI can cast again 2 s later; the last use adds nothing and the full
cooldown runs. There is no 12 s window (a lapse cannot add cooldown back), which the AI does not need: it spends the
recasts as champions come into reach.

**Venom stacks that burst on each enemy (league_twitch passive and E, Deadly Venom and Contaminate).** League's venom
sits on the enemy, six stacks at most, and Contaminate deals damage per stack on every poisoned enemy. Nothing reads a
buff count on a target, but `AddCasted` never refreshes or replaces: every hit (the bolt's twin on `EnemyWithoutTower`,
the cask, its puddle, R's bolts) hangs two instances on the unit it hit - the venom (`Poison`, 360 ticks, true damage
every 60: the poison icon) and a watcher (period 2, 360 ticks) whose effect is `SwitchByBuff e_pop` -> the per-stack
burst (an `Attack` and its picture). E raises the caster flag `e_pop` for 3 ticks (league_ryze's Flux window): every
watcher on every unit sees it exactly once, so each enemy takes the burst once per stack it carries. Measured with
instrumented watchers (each burst and each venom tick adding a caster buff): the bursts of an E equal the live stacks,
4 = 4, 5 = 5. Limits: no 6-stack cap (fast attacks reach 8-9) and no range (every poisoned unit on the map bursts).
His E's takedown (Ambush's reset) is league_jinx's kill check laid on every champion within reach around the burst.

**Camouflage broken by the first shot (league_twitch Q, Ambush).** league_evelynn's poll: the cast sets `q_on` (q_t)
and an `AddCasted` on him that, every q_poll ticks while `q_on` holds, renews `CasterInvisible` for q_poll + 2 and the
move speed; every attack, skill and ult first checks `q_on` - present: removed (the camouflage lapses within a poll)
and the attack speed buff given. The cast is a `Targeting` slot on `EnemyChampion` at 90000, farther than his attack,
so the AI hides as it closes in. The combo: the revealing attack throws the cask (W's cooldown is a caster flag too)
when it is ready.

**Piercing bolts while the ult lasts (league_twitch R, Spray and Pray).** `range` and `attack` on a caster buff r_on,
and the attack branches on it: a tick-1 `TargetProjectile` probe on `EnemyWithoutTower` adds a flag (it must outlast
the shot's tick: a 4-tick flag read on tick 7 never fired a single R bolt in the first draft), then at the shot either
a penetrating `LinearProjectile` on `EnemyWithoutTower` toward the target (115000 long) or, for a tower, the plain
bolt. The falloff (100 / 90 / 80 / 70 / 60%) is a ladder of 30-tick caster flags cleared at each shot. The slot is
armed like league_samira R: a cast fires at once with two enemy champions within 85000, else arms 600 ticks during
which his attacks count again and, after 180 ticks, fire with one champion in reach; a lapse refunds the cooldown.
With the two-champion rule alone R fired 1-3 times in a 10-minute game.

**Every third spell cast twice, and notes for the next attack (league_seraphine passive, Stage Presence).** Each cast
(Q, E -> W, R and the combos' casts) climbs a caster ladder `c1` -> `echo` (`Permanent`, its own picture under the
stage); a cast that finds `echo` removes it and plays the same effect again `echo_delay` (12) ticks later from a
`Delayed` - the play is in the tree twice, not three times (normal, echoed and copy). Q leaves a ready echo alone for
`echo_hold` ticks (a 300-tick flag laid with it) so the echo goes to E -> W or R. The notes are a second ladder `n1`..`n4`
(360 ticks, each carrying `range` +3000): every cast climbs it once, and once more for each allied champion within 60000
(the climb inside a `RangeEffect` on `AllyNotSelf` runs once per ally); the next attack reads it from the top, removes
it and sends a charged note (k x note damage) instead of the plain one.

**Slowed -> rooted, CC'd -> stunned (league_seraphine E, Beat Drop).** Nothing reads a slow on the target and the echoed
wave is the only one that can find her own slow still on it, so every champion the wave hits carries a mark: a
`Delayed {tick: 4}` `AddCasted` poll (period 2, 90 ticks) whose effect is `SwitchByBuff e_rt` -> `Bind` 45. A champion
hit by a wave sets `e_rt` for 3 ticks only while the caster flag `e_2nd` holds, which the echoed copy lays before it
flies (the `copy` argument of the cast wrapper): the first wave marks, the echo roots what it marked. The 4-tick delay
keeps a wave's own mark from reading the `e_rt` its own later hits set (a two-champion line rooted the first one
otherwise). The stun is a twin wave with `applied_target: EnemyChampionInCC` (charmed by R, rooted, anyone's stun),
named apart (`e_cc`) so no picture rides on it - a projectile named like a `ViewEffect` would carry that picture.

**A line that reaches farther past an ally (league_seraphine R, Encore).** A hidden `LinearProjectile` probe on
`AllyChampion` at 60000 a tick runs the wave's line first and sets `r_ext` on her when it touches an allied champion
(it never touched her at its start: 0.25 extensions a game, none without an ally ahead); 2 ticks later the wave flies
150000 with the flag, 90000 without. The slot is armed like league_twitch R (two champions within 70000 at once, one
in attack reach after 3 s, else the cooldown refunded); the armed check rides only on the attack (in the skills it
copied the whole ult into trees cloned every tick: 6000+ nodes).
**Fury that empowers the next skill (league_renekton passive, Reign of Anger).** League's 50 Fury is five rungs of one
exclusive caster-flag ladder f1..f5 (league_twitch's venom ladder, about 20 nodes): a gain steps one rung up and runs
the hold again (480 ticks); the hold lapsing drops it all (League's out-of-combat decay in one step - the cumulative
ladder of league_tryndamere, every lower rung a step longer, cost three times the nodes in every gain). Gains: his
attack, Q's champion hits (one each) plus one for the rest (a 2-tick flag any hit lays, read a tick later), every unit
Slice passes, W when not empowered, R two on the cast and one a second. Each skill branches on f5 at its first tick:
empowered, it spends the ladder. Q takes it only while W's caster flag (its slot cooldown) is on, so the AI keeps a
full Fury for W's 1.5 s stun (the pro rule). League's +50% Fury below half health needs his health: a native add-on.

**Dash, chop, dash back (league_renekton E -> W -> Dice).** One `Targeting` cast on `EnemyChampion`: Slice is a
`RushTime` through the target (penetrate, a Fury rung and a 240-tick `d_open` flag per unit hit); on landing W fires two
(three) instant `TargetProjectile`s at the target 7 ticks apart on `EnemyChampion`, the last carrying the `Stun` and its
stars buff; then, when Q's own flag is off, Q (E -> W -> Q, the heal right after the stun) and Dice: a `RandomTarget`
on `EnemyChampion` holding a second `RushTime` (empowered: an armour shred buff `defence_mult` -25 instead of the rung).
Q's slot keeps that flag too, and a slot cast inside it is a 1-tick nothing. The combo's Q branch is the plain and
empowered copies only (W's flag is on there), keeping skill2 at 309 nodes. As crowd control for league_yasuo's R: with
him top in Yasuo's team, R on champions 2.40 a game (the base fighter 2.12, league_darius 1.31) - no change.

**A transformation armed for the fight (league_renekton R, Dominus).** Armed like league_twitch R: within 35000 of an
enemy champion it fires at once, else his attacks fire it for 600 ticks (refunded when it lapses). Fired: `r_on` with
flat `hp` +300 for 600 ticks and a `Heal` of the same 300 (the bonus health starts full), two Fury rungs, and two
`AddCasted` on him (`on_me`): a 30-tick pulse of `ApAttack` 15 + `hp_ratio` 1 (1% of his maximum health) round him on
`EnemyWithoutTower`, and a rung every 60 ticks. No size change (the sand aura is a view buff behind him).

**A damage over time that also counts on champions (league_lillia passive, Dream-Laden Bough).** Every ability hit
leaves Dream Dust: an `AddCasted` of `Poison` kind (d_t ticks, a run every d_period) with magic damage on anything and,
on `EnemyChampion`, a twin dealing `hp_ratio` 1 a run as TRUE damage (`ApAttack`'s max-health part ignores magic
resistance: League's 5% magic is the add-on's) and healing her once per champion hit. The champion twin is also R's
listener (below). Each cast climbs Prance, an exclusive caster-flag ladder p1..p4 of move speed (league_twitch's way).

**An outer ring that hits harder (league_lillia Q, Blooming Blows).** Data has no "outside radius r_in" target. Q hits
everything in q_r with magic damage; the inner circle first gets a 1-tick `damaged_reduce` 99 buff (q_in), then the
edge hit lands on everything in q_r again as true damage (a 1-tick full magic penetration on her), so only the ring
outside q_in takes it. The dust in Q is delayed a tick: its first run would land under the inner buff.

**A thrown seed, then a strike that lands where the target stood (league_lillia E -> W).** E is a `ParabolicProjectile`
lob onto the target (magic, slow, dust); once the throw ends she winds up (`skill2_w`) and W's strike is another hidden
lob of w_wind ticks aimed at the target's position, its warning ring a `ViewEffect` on the point (never turned); the
landing hits round it and a second, smaller lob (w_sweet) adds the sweet spot's extra damage - the slow from E keeps
the target on it. League's seed rolls on after a miss: a projectile started from a landing flies from the caster
again (logged), so the roll is left out.

**A sleep on everyone she dusted (league_lillia R, Lilting Lullaby).** Data cannot find "every champion with my buff".
R sets a caster flag r_go for one dust period; every champion's dust twin, on its next run, reads that flag on its
caster and applies drowsy (a slow, r_drowsy ticks) then a `Stun` (r_sleep) with the sleep's picture - league_ryze's
flux trick. The slot is armed like league_seraphine R (two champions within reach with dust lately, or one after
r_hold) and refunds the cooldown when unused. Her own Q / W on a sleeper within the window add the wake damage;
damage breaking the sleep (League) needs the native add-on addons/league_lillia, whose passive reads r_go's rising
edge, sleeps the dusted champions with `apply_cc` and clears it when their health and shield drop. As crowd control
for league_yasuo's R: with her jungling in Yasuo's team, R on champions 1.27 a game (the base
ninja 0.58, league_leesin 1.67, league_kayn 1.00) - no change.

**Upgrades by level, re-read every life (league_viktor passive, Glorious Evolution).** League counts Hex Fragments
across deaths; data cannot (death clears a mod's caster buffs), so the four upgrades come by level through
league_khazix's probe on the attack - with his attack as the gauge: every base mage and league_brand buy only ability
power items in the SDK (their item events), so a mage's attack is atk + atk_g a level and nothing else. Under 2 ticks
of `damaged_reduce` 99 and `defence_penetration` 100 a 1-run `AddCasted` `Attack` of 1000000% (100 x his attack after
the cut; damage over time never crits) against a 3-tick shield halfway below the level. His own Q shield blocks a probe
(the WithShield guard), so it simply waits. Each life's first attack opens a 900-tick quiet window in which the next
stage is probed every 40 ticks without the gold flash. In logged games the stages came at levels 3 / 5 / 7 / 9 and came
back silently after each death.

**A line that starts on the target (league_viktor E, Hextech Ray).** League starts the ray at a chosen point and sweeps
it on. A `LineRangeProjectile` started in a lob's `end_effects` does NOT start there: its hit segment runs from the
caster (the lob's spawn; logged `from` = his position, `to` = 70000 ahead) while its view is drawn at the landing point
(the projectile's x, y) turned from him to it - a short test (length 20000, width 1000) hit only minions beside him and
never the target 60000 away, with a 3-tick lob too. So the hit is a `RangeProjectile` with a `DirDot` shape on the
landing point (radius 70000, range 985: a cone about 10 degrees each side opening away from him; the unit standing on
the point is inside it - the target was hit on 49 of 49 casts; a circle on the point as well hit it twice in a quarter
of the casts), and the picture is a hitless `LineRangeProjectile` (applied to `Ally`, nothing applied) whose cell is
twice the ray's length with the beam drawn in its right half from the centre. The aftershock is the same pair in a
`Delayed` of the `end_effects` (the point is kept).

**A storm that rides a champion and moves on when he dies (league_viktor R, Arcane Storm).** league_annie's Tibbers:
a lob bursts round the target, then an `AddCasted` (period 60) on him runs a picture over him and a 1-tick lob whose
circle hits everyone round him. Each run's landing also leaves a hidden `RangePeriodProjectile` (radius r_jump_r, tick
62, period and first_delay out of reach) whose `end_effects` - applied to every enemy champion inside when it ends -
move the storm to the first of them when the caster flag `r_live` is missing: the next run renews it, so only a target
that died since leaves it gone. A 2-tick `r_live` gave false moves (the zone ends a tick or two after the next run):
6 ticks. The move takes a lock and reads it back in the same tick: a dead caster's flags freeze and nothing can be
added, so no storm moves (or doubles) while he is dead. Moves nest linearly (the evolved size chosen once at the cast:
branching on it at every level made the tree exponential, 4 MB); two moves keep the ult at 662 nodes. In 4 logged games
every move followed a champion's death.

**A native effect that reads the unit a hit landed on (addons/league_fiora_duel, addons/league_vayne_bolts).** Data
cannot tell which unit a hit is on (league_vayne's Silver Bolts, league_fiora's Vitals both count on the caster). A
`Native` effect (`effect_ref`) placed in a projectile's `applied_effects` gets that unit as its input target
(league_pyke's execute, confirmed in game), so it can read the unit's buffs: Fiora's copy adds a target buff
`league_fiora_r_mark` where R starts and the native `vital` adds the 3-tick caster flag `r_tgt` only when Fiora's
R is on and the unit hit carries the mark; Vayne's native `bolt` counts `league_vayne_bolts_s` instances on the unit
hit and adds `sb_r1` / `sb_r2` / `sb_go`. The data reads the flag in the same `Combine` and, when it was not there yet,
once more a tick later (a `Delayed 1`): whether a buff the native adds is visible to the data in the same tick is not
proven in game. The data halves were checked in the classic sim with the `Native` node swapped for the flags it sets.

**Feathers that lie where a blade stopped and fly back on a recall (league_xayah Q, passive, E).** A feather is the
stop point of a penetrating `LinearProjectile` (a dagger or an empowered attack's line): its `end_effects` stamp a
`ViewEffect` there every f_step ticks (so it vanishes the moment it flies) and poll a caster flag `rc`; the only
projectile that leaves from a point is a `BackToCasterLinearProjectile` in a projectile's end_effects or a `Delayed`
there (league_ekko Q, league_pyke E), so that is the flight back. Nothing waits for an on-demand E: the recall is a fixed
moment - Q sets `rc` (f_step + 1 ticks) q_recall ticks after its release, R r_recall ticks after the rain. League roots
an enemy hit by three feathers; nothing counts hits per target, so the count is hers: caster flags rh1, rh2 climb on
each champion hit of one recall and the third hit onwards roots.

**A spell that empowers the next attacks (league_xayah Clean Cuts).** Every spell climbs a caster-flag ladder p1..p5
(League's store of five, p_t ticks); the attack's `SwitchByBuff` on p1 fires a homing blade for the target's 100% (a bare
line missed walking targets: -0.68 -> +0.85 in the sim) plus a penetrating line a_reach long that hits the others for
a_pierce% and drops a feather where it stops, then steps the ladder down.

**A duo read off buffs the partner puts on you (league_xayah + league_rakan).** No selector picks an ally by who he is
and `SwitchByBuff` reads only the caster's own buffs - but a buff another hero's kit adds to him is his own buff:
Xayah's attack adds `league_xayah_duo` (duo_t ticks) to allies within duo_r and her W `league_xayah_duo_w` within
duo_w_r; Rakan's kit (patched by tools/fix/rakan_xayah_duo.py) branches on them: W's attack speed and second feather,
a fourth E ring that reaches her, his Xayah voice line. Without her the buffs never exist, so his games are unchanged
(checked in the sim). lint_mod.py reports a buff added by another hero as info, not as a missing buff.

**An ult held for a fight (league_xayah R).** `EnemyChampionRecentlyAttacked` within 60000 instead of any enemy champion
within 85000: 3.3 casts a game, 1 of 40 with no champion under the rain (6 of 58 before), 1.5 champions a cast.

**A spell with no slot that fires itself (league_vladimir W, Sanguine Pool).** The pool is a data tree started from a
poll: every attack and spell adds, unless the caster flag `polling` is on, an `AddCasted` on himself (36000 ticks,
period 3) whose effects refresh `polling` (period + 2 ticks, so a poll that ended with his death is started again by his
next attack) and run the pool when `w_go` is on and `w_cd` off. Anything may set `w_go`: the main pack's attack runs
league_tryndamere's danger check (two enemy champions within d_near, or the 1-point-shield hit sensor at h_n checks in a
row); the add-on's native passive (addons/league_vladimir_pool) sets it below 35% health. The pool itself: a 2-tick
`undying` flag around a `FixedAttack` hp_ratio on himself (the health cost never kills), `CasterInvisible` + a caster flag
with damaged_reduce 100 and cc_immune (league_xayah R), `CasterAnimation skill_w` for the whole time, pulses in
`Delayed`s. 7 pools a game in the sim.

**A drain whose blood flies back (league_vladimir Q).** The damage lands on the target in the cast; a hidden
`ParabolicProjectile` with travel_time 1 lands on the target's spot and its end_effects start a
`BackToCasterLinearProjectile` from there, whose own end_effects heal him when it arrives (league_xayah's feathers).

**Combos played by the slot they spend (league_vladimir).** E -> Q: a champion-only twin of E's bolts adds `eq`; Q's tree
branches on it before the Crimson Rush counter. E-W: the pool's last `Delayed` runs E's nova at 70% when `e_cd` (set on
every E for its cooldown) is off. Flash R E: R with `e_cd` off adds a hidden `LinearProjectile` on EnemyChampion whose
radius stops it r_stop short of the first champion; its end_effects `Teleport` him there (league_lissandra E), and a
`Delayed` nova follows the cloud. None of them spends E's cooldown (league_leesin_combos: an empty branch cannot hold a
slot).

**An empowered attack that runs itself, and its triple (league_rengar Q, Savagery).** No slot: the attack's tree picks
`ready` (the pounce) > `f4` (four Ferocity: the empowered Savagery, which spends them) > `q_cd` off (Savagery: the Q
strip, the slam and rip as homing hits, then attack speed) > the plain swing. The Savagery that fills Ferocity puts its
cooldown on `q_hold` instead of `q_cd`: `q_hold` stops only a plain Savagery, so the next attack is the empowered one at
once (League's triple Q) and the empowered Savagery appears once in the tree (twice it cost 60 nodes; one kill read for
all the attack's branches cut the tree from 351 to 242).

**Two kits that talk (league_rengar <-> league_khazix, the rivals' easter egg).** A `SwitchByBuff` reads only the
caster's own buffs and nothing tells which unit died, so each kit marks what it hits (`AddBuff league_rengar_rival_hit`
on champions) and each action of the other answers when it finds the mark on itself, by marking every enemy champion
near it (`league_khazix_seen`); a kill check (league_jinx's) that fires while the caster holds the answer is the rival's
death. First sight: each action marks the enemy champions near it (`league_khazix_near`), the other plays its line once
a life. A teamfight kill of someone else in the 1-second window counts too - fine for an easter egg.

**Something that happens when he dies (league_kogmaw passive, Icathian Surprise).** No data effect runs on a death. Each life's first action (a `Permanent` caster flag death clears) starts a whole-game `AddCasted` on him (period P) that lobs a hidden `ParabolicProjectile` onto himself (`applied_target: AllyOnlySelf`, no applied effects) flying P + 1 ticks; its `end_effects` ask `RandomTarget {range: 1, casting_target: AllyOnlySelf}` for a 1-tick flag (no dead caster is found) and, without it, start the death effect. The `AddCasted` stops with him, so exactly one lob in the air finds him dead; travel P (not P + 1) missed the deaths on the landing tick (the check ran before the death, 6 of 14 lost), P + 1 caught 14 of 14 with no double. A burst where he fell hit nobody: a ranged hero dies 20000-150000 from the enemies. The void form is a visible `TargetProjectile` (1800 a tick) plus a hidden `TargetSplashProjectile` at the same speed for the burst (league_jinx's rocket), both in a `RandomTarget {EnemyChampion, from_projectile: true}` within 70000 of the landing: projectiles started from another projectile's `end_effects` spawn after the caster's death, also in the SDK (12 of 14 reached a champion and burst; the two lost ones were out of sight when they arrived).

**An axe he runs to catch (league_draven Q, Spinning Axe).** The empowered attack's hit runs, a tick later (a
projectile in a projectile's `applied_effects` needs the `Delayed`), `RandomTarget {range: 60000}` on
`EnemyWithoutTower` - every other bounce on `AllyNotSelf` first (a toggle flag; a 1-tick flag says one was found) - and
inside it two hidden penetrating `LinearProjectile`s at that unit with `y_offset` 5000 (so they leave from his own
spot): one as fast as it is long (18000 or 24000), which ends the tick it starts, and one that takes the fall (24
ticks). The fast one's `end_effects` run on its end point: the catch circle and the falling axe as `ViewEffect`s there
(not his own spot, so they show), `CasterAnimation run` and `MoveTo {speed: far / 21}`: **`MoveTo` in a line's
`end_effects` dashes the caster to that point** (ForceMove steps of exactly `speed` toward it, ending on it). The slow
one's `end_effects` ask `RandomTarget {range: 4000, casting_target: AllyOnlySelf, from_projectile: true}` two ticks
after he gets there: in the SDK 100 axes of 100 caught, standing on the spot (median 0 units off). Before
(2026-10-10, first version) the axe fell where he stood when it hit and the AI never walked to it: 8 in 10 caught,
most of them with him already out of the circle (13600 units off the centre, the check's range counting his body). A
forced `CasterAnimation idle` holding him under a 42-tick fall kept him in the circle too, but it blocked his next
attack by up to 20 ticks, so the fall became as long as the run. With nobody near, the old way: a lob onto himself, the
circle a non-following `CasterViewEffect`. Measured on the way: a `LinearProjectile` in a `LinearProjectile`'s
`end_effects` starts at the caster (heading for that end point), not at the end point - only the
`BackToCasterLinearProjectile` starts there. Blood Rush has no slot (League's W has no cast): the attack turns it on
when its cooldown flag is off and an enemy champion is near, and a catch removes the flag - the juggling loop.
Whirling Death turns back at the first champion: a non-penetrating line on `EnemyChampion` (seen) whose `end_effects`
start the `BackToCasterLinearProjectile` back, beside a hidden penetrating line for the damage on the way out. **A
line's goal (its start + direction x `range`) is clamped to the map one axis at a time - `Targeting` casts too - so a
line whose goal falls off the map bends**: League's global R at range 1000000 bent 9-13 degrees and missed its target
(one went to the map's corner, 959999 x 0); at 400000 the casts measured bent 0-4 degrees, so the blades fly 400000
(radius 16000, League's width) from casts on champions within 250000 *(SDK simulation, 2026-10-10)*.

**A shadow that copies the combo (league_zed W, Living Shadow).** Every projectile leaves from the caster, and a zone's
applied effects cannot start anything at the zone's point (measured 2026-10-09 with work/zd/test_echo.py: a
`BackToCasterLinearProjectile` and a `RangeProjectile` in the applications of a `RangePeriodProjectile` on `AllyOnlySelf`
never spawned; a lob there left from the caster). Only a projectile's own `end_effects` act at its point, and a `Delayed`
among them keeps the point. So the shadow is a hidden lob (`travel_time` 4) onto the champion's spot: its `end_effects`
hold the picture's pieces, the copies of the same cast's slash (a zone on the spot) and shuriken (a
`BackToCasterLinearProjectile` from the spot back to Zed, through the champion standing on it), each gated by a 3-tick
flag his own slash / shuriken set a tick before, and the checkpoints of the swap (`Teleport`). The user then asked for League's shadow (「你可以增加节点 实现成原样的」): every later Q / E is copied at the
next checkpoint, a `Delayed` every 12 ticks (W) / 6 ticks (R); his slash and shuriken set the shadow's flag for
exactly one step, so exactly one checkpoint copies each and nothing has to spend it; the combo's own copies use
their own flags (`ec_echo`, `qc_echo`). W's tree is 593 nodes (the engine copies it every tick); the R shadow's
checkpoints sit in the ult's tree, which it does not copy. In the SDK 56 of 58 later shurikens and 55 of 58 slashes
were copied, most within a tick, the last 12 ticks late.

**Slots whose cooldown is a flag cost the AI's walk (league_zed draft, 2026-10-09).** W and Q started as 60-tick slots
with their real cooldowns in caster flags (empty branches while a flag ran, league_leblanc's way): the AI cast the
ready slot every second, walked at the enemy champion to cast W, farmed 58 attacks a game and went -3.8. Give a slot
its real `cooltime`; keep a flag only where another action must know it (Q's slot under the mark with W ready).

## 8. Gotchas

**A native view effect played on a fixed map point draws once (league_nocturne_dark 0.4.0 -> 0.4.1, 2026-10-09).** `StableSim::play_view_effect` with `InputTargetV1::pos` at the map centre returned true and the sim logged the veil on every ult, but the client darkened the screen only on the first one (「第一个大是会黑的」). Played on Nocturne (`InputTargetV1::target`, the view `is_follow: false`) every layer shows (15 ults, 45 layers, 「每次都黑了」). Play native pictures on an entity, never on the same point twice.


- A `RangePeriodProjectile` put straight into an action's effects, or into a self-only `RangeEffect`, is never
  created (league_nocturne W's poll: no zone in the logs, no attack speed in nine games); zones start from a
  projectile's `end_effects` - a hidden 1-tick `ParabolicProjectile` onto the target does it (league_ekko's zones,
  league_nocturne's poll).
- The engine copies the `skill` / `skill2` trees every tick (the perf session's tick meter, 2026-10-02): league_nocturne
  E's 15 `Delayed` guard checks and 10 `Delayed` tether links (260 nodes) made a game with one Nocturne cost 1.38x a
  base game's CPU per tick; written once - one polling zone and one `AddCasted` (56 nodes) - 1.17x. Write repeated
  work once instead of a `Delayed` per pulse.
- `action_name` / `CasterAnimation.name` must be real sprite tags. Two LoL Reborn heroes use
  `action_name: "skill"` while their sprites only have `skill1`.
- `SwitchByBuff` checks the caster; the buff must be added somewhere in the same kit.
- An `ult` with `Targeting` on `EnemyChampion` is cast in nearly every fight, as the hero closes in (league_kayle
  R: about 5.6 times a game in the simulation, against 0.25 for a probe ult cast on `AllyChampionInCC` with base
  teammates); its effect can then pick an ally (`RandomTarget` `AllyChampionInCC`). An ally-targeted ult is cast
  whenever it is ready, on whoever the AI picks - not the most injured (section 3). To wait for a moment in the
  fight, arm it and check from the attacks (section 7 "An ult that waits for danger").
- Keep `start_timing <= duration`; long channels need a long `duration` (or `Delayed` effects).
- Use namespaced names for every buff/projectile/effect (`league_garen_*`) - names are global-ish
  and collisions with other mods are hard to debug.
- Custom sounds must be injected with override entries or `Sfx` will not find them
  (see `text-audio.md`).
- The engine plays `<champion id>_attack` on every basic attack by itself; never play that name
  from the effect tree too (see `text-audio.md`).
- A `Delayed` `FixedAttack` on a unit the caster's team cannot see (fog) dealt no damage in the
  simulation: late hits are lost on a target that fled out of sight (league_yone's echo, section 7).
- **A picture-only projectile still makes the enemy AI dodge** *(SDK simulation, league_missfortune R,
  2026-10-01; 144 games a variant)*. Her wave picture is a `LineRangeProjectile` with no `applied_effects` that never
  applies (100000 x 36000, delay 15, apply 65); on `EnemyWithoutTower` the enemy champions standing in it stepped
  about 4100 units sideways each wave and out of her cone (4.75 champion hits a cast; 1000 wide 5.55, no rectangle
  at all 6.40). On `applied_target: Ally` it draws the same and they moved 1800 (normal fighting), while her allies did
  not start dodging it (1600 -> 1700): 7.12 hits a cast with the 50 degree cone, 5.06 with the same cone on
  `EnemyWithoutTower`. Put a picture that stays while damage comes later on `Ally`.
- **Keep a line's goal on the map** (section 4, "Where a line ends"): a `Direction` or `Targeting`
  `LinearProjectile` whose goal (the caster + direction x `range`) falls off the 960000 x 960000 map is turned toward
  an edge or a corner. League's global ults at `range` 1000000 (league_jinx R, league_ezreal R) turned 7.5-9 degrees
  in the median and up to 45-56; at 300000 six lines in seven fly true. A global skillshot cannot fly straight; a
  `Position` cast is straight but stops on the cast point.
- **Keep a skillshot's damage where the enemy AI can see it** (same section): a line whose damage sits behind a
  `SwitchByBuff` on a caster flag is not dodged - league_jinx R's blast gated that way struck 80% of the time instead
  of 67%. Start a follow-up that must wait for the hit from the hit itself (a `Delayed` hidden lob onto the unit).
- **A projectile must end** *(SDK simulation + stack sampling, league_fiora W, 2026-10-02)*. Her guard picture
  was a `TargetProjectile` at speed 100 with no `applied_effects`: it trailed its target for minutes (one lived
  11214 ticks). Each tick a projectile runs, `prepare_dead_caster_overlay` copies its caster's whole entity
  (all four effect trees) when that caster is dead - so once Fiora died the match's CPU per tick tripled and
  stayed there. Give picture-only projectiles an end: a `LinearProjectile` with `range` = speed x ticks the
  picture shows (hers: speed 100, range 4500 = 45 ticks), on `applied_target: Ally` (previous entry). lint warns
  on a `TargetProjectile` slower than 1000 and a `LinearProjectile` alive over 600 ticks.
- **skill and skill2 are copied every tick** *(same study)*. While a match is on screen,
  `build_entity_state_event` calls `skill()` and `skill2()` for every champion each tick, and for a data
  champion that clones the whole action with its effect tree. 55% of a Jinx mirror game's CPU went to copying
  her 1019-node skill2; ten league heroes cost about 4x the CPU of ten base champions per tick (background
  matches, which build no events, only +8%). Attack and ult size do not matter here. Keep skill/skill2 lean:
  one animation instead of a frame-by-frame `Delayed` + `ViewEffect` chain, shared logic outside copied
  `SwitchByBuff` branches. lint lists skill/skill2 above 300 nodes as INFO.
- A buff's view can outlive its unit: Garen died mid-spin and the whirl of his 3 s caster buff
  stayed on the body (no view_buffs option covers death). For a purely visual timed effect,
  play `CasterViewEffect` on a timer instead (one per `Delayed` pulse, `is_follow: true` in
  `view_effects`); keep buff views for states that must vanish on consumption (Q ready).
- Run `python scripts/lint_mod.py <mod>` after every edit.

## 9. Checking a fact against the engine

**Which SDK (game 0.6.2, 2026-09-30).** The classic SDK, the one that ships the engine, ended with game 0.5: the
official docs (teamsamoyed/TeamfightManager2Mod) call it deprecated, "supported through game version 0.5 only, and
no longer shipped or updated from 0.6". The game folder keeps `mod-sdk` (its `base_version.txt` says 0.5.0, but its
game_core is the 0.5.1 build, the same file as in `mod-sdk-0.5.1-package`) and, since 0.6, `mod-sdk-stable` (0.6.2):
the stable-ABI API for native DLL mods (`mod-api-stable`, plain Rust with no engine inside; its `sim.rs` only reads
the match the game is running). A data-only mod needs no SDK at all. So the probe below and the simulator
(porting-heroes "Balance check") stay on game_core 0.5.1, the newest engine a program can link. The data they
load from bundle.game_data (champion sheet, game / item / map settings, macro weights) was compared byte for byte
with the 0.6.2 bundle: identical. Engine code changed after 0.5.1 is not in them; for what the 0.6.2 loader accepts
use the official schema (docs/data-champion-schema) together with the probe. Every effect type and field this pack
writes is in that schema or named in the 0.6.2 binary (`CasterInvisible`, the `cooltime_use_count` action field and
`LinearProjectile.y_offset` are undocumented there but still read); the one dead key it wrote, `is_hidden` (35 buff
states in league_darius, league_leesin, league_lux, league_soraka and the template), is gone, and `lint_mod.py`
warns about it and knows the 0.6 additions (named passives, `Rush`, `ShrinkingBarrier`,
`TargetProjectileFromProjectile`).

The mod SDK in the game folder ships the engine itself: `mod-sdk*/deps/libgame_core-*.rlib` (+
`.rmeta`, serde_json next to it) built with the toolchain pinned in its `rust-toolchain.toml`
(`nightly-2026-05-24`). Two ways to ask it:
- **Parse with the official data types.** `scripts/sdk_probe.rs` deserializes a whole
  `.data_champion` (`game_core::DataChampionInfo`) or single effects, one JSON per line
  (`game_core::DataEffectDef`), and prints serde's error or the parsed value with every field and
  its default - an unknown variant error lists all accepted values, a field missing from the output
  is one the engine ignores (that is how `DirDot`, `Forward`, `Bleed`, the `attack_ratio` default
  and the ignored `is_hidden` were found). Build and run it as the file's header shows.
- **Read the code.** `llvm-nm -A --defined-only` and `llvm-objdump -d -r --disassemble-symbols=<mangled>`
  from the same toolchain (`lib/rustlib/x86_64-pc-windows-msvc/bin`) on the object files inside the
  rlib (`llvm-ar x`): each effect is `<...Effect as EffectType>::apply`, the per-tick logic is
  `Entity::run`. Slow but decisive; mark such facts "read from the SDK's game_core" until seen in game.
