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

The game binary also names `passive`, `passive_skill2`, `passive_ult`, `stack_skill_index` and
`name`, but the mod SDK's `DataChampionInfo` (what a mod's file is parsed into) has none of them:
its fields are exactly the ones above plus `skill_icon`. There is no "on spawn" hook either, so build
passives with buffs (section 7); a permanent one goes on at the first action (league_amumu's Tantrum
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
  (a per-team timer on the target, `CastingTarget::check`), not one the caster hit itself.
  `EnemyChampionInCC` / `AllyChampionInCC` is a champion carrying one of six crowd-control states
  *(read from the SDK's game_core: `CastingTarget::check` tests the target's CC list against mask
  0x347)*: airborne (`Airborne`), stun, root (`Bind`), forced movement (`Knockback`, `Pull`, `Grab`),
  fear and charm. Disarm (`BlockAttack`), silence (`BlockSkill`), `BlockMoveSkill`, taunt and slows
  (slows are buffs) do not count, and no target narrows it to knock-ups only: league_yasuo's R, cast on
  `EnemyChampionInCC`, also fires on stunned or rooted champions. No base champion's data uses it.
  As a projectile's `applied_target` it is tested when the projectile hits (league_fiddlesticks Q,
  section 7).
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
  normally (`is_follow` false by default). The view layer's effect system carries an `is_rot` flag, so it
  probably turns a picture on a point toward it from the caster, which has no direction at zero distance
  *(inferred)*. Play such a picture as a `CasterViewEffect` in the cast (not following), and keep
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
  there, which hits the next tick - an area round a unit wherever it walks (league_annie R). A dead caster
  fires no projectile, this one included.
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
  with `speed` 1, `range` 1, section 7 "Back to where he stood").
`ApplyInProjectile` has no `period` and `RangePeriodProjectile` no `follow_caster` (SDK), so an aura
that ticks while it follows the hero is built from `Delayed` pulses of a `RangeEffect` around the
caster (section 7, "Aura that runs while he fights").

Shapes *(`ProjectileShape::is_in` in the SDK's game_core; every radius and half-size also counts the
collision radius of the unit tested, and for RangeEffect the caster's too)*:
- `{"Circle": {"radius": N}}`
- `{"Rect": {"width": W, "height": H}}` - axis-aligned around the centre, never turned
- `{"Line": {"width", "from_x", "from_y", "to_x", "to_y"}}` - a segment with fixed coordinates: they are
  map positions, not offsets from the projectile, so no wall can be drawn round where a hero stands
  (league_thresh R's five walls became one circle)
- `{"DirDot": {"radius": N, "range": C}}` - a **cone**: within `radius` of the centre and at most
  acos(C / 1000) off the direction from the caster to the centre (`range` 600 = 53 degrees each side).
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

**Base only - do not use in mods:** `Native` (calls hard-coded logic via `effect_ref`),
`ShrinkingBarrier`, `AddStatScaledBuff`, `Rush`.

## 5. buff_state

```json
{"name": "league_garen_q_haste", "duration": {"Time": {"tick": 90}}, "move_speed_mult": 35}
```

`duration`: `{"Time": {"tick": N}}` | `"Permanent"` | `"WithShield"` (lasts while the shield
holds). Some pack buffs omit it - set it explicitly. *(seen in the SDK simulation, league_annie E:
a `WithShield` caster buff added right after her own `Shield {tick: 180}` was gone 180 ticks later
when nobody hit her, and 89 ticks after the cast when enemies broke the shield first.)*

**`WithShield` to the tick** *(SDK simulation, league_kayle)*: a `WithShield` buff stays while any shield on
the unit holds - also one an ally gave it - and is gone 2 ticks after the hit that breaks the shield, so read it
with a `Delayed {tick: 2}`. A `FixedAttack` on yourself is scaled by `damaged_reduce` / `damaged_amplify` like any
damage, and damage a shield absorbs does not count in the simulation's "tank" statistic. A dying caster's
zones and pending `Delayed` effects stop; the respawned hero is a new entity with none of them.

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
  once, so its frames cover the zone's lifetime).
  A `CasterViewEffect` is not turned: it is drawn at the caster's pivot, mirrored when the caster
  faces left (the base gunner's backward-run dust is drawn only behind him), and stays where it was
  played unless `is_follow`. An `Animation` plays its tag once, so a view that must stand for
  seconds lists its loop frames again (a 4 s loop of 100 ms frames is 40 frames).
  A thing with a top and a bottom that flies every way (league_thresh's lantern) is laid along its flight
  and mirrored top to bottom, so every turn of it looks the same (art-spec).
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
`casting_type: Direction` action is a rectangle from the caster toward the target, and its view
sprite is centred on the rectangle and turned to the cast direction: drawn pointing right from
x = -length/2 to +length/2 (measured on LoL Reborn's Swain Q fan, Lux R and Jhin W sprites). So a
fan sprite with its apex at x = -length/2 starts at the caster. The hit area stays a rectangle;
draw the fan a little wider than `width` (oppi's Swain does). league_ashe W: width 45000, length
80000, delay 17, apply 14 (the hit at tick 13, when the arrows have flown out; until 0.10.0 delay 14,
apply 3 hit at tick 2, as the fan appeared), 9 arrows over +-28 deg, 7 frames x 40 ms, view `repeat: false`.

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
  (x at 960000), which turned it further;
- `y_offset` on a `LineRangeProjectile` is ignored (the line does not move);
- a `LineRangeProjectile` started in a projectile's `end_effects` is drawn at that point but points from the
  caster to it (from a point above him: straight north);
- a `TargetProjectile` (and a `TargetSplashProjectile`) stays at the caster's pivot in the logic - its
  `y_offset` only lifts the picture, `5000 - y_offset` above the pivot like a `LinearProjectile`'s start
  *(inferred: the base heroes' 1200, 1500, -3000 and -4000)* - and points at its target from there, so its
  picture runs level with a line cast at the same target. But it goes the tick its target dies.
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
100000, range: 940}` (a 40 degree cone toward the cast point) for the damage and a view-only
`LineRangeProjectile` (100000 x 36000, delay 15, turned to the cast point) for the picture.

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
minion. Cast it on `EnemyWithoutTower` so it is also used on waves and camps (on `EnemyChampion`
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
most one attack. Each pulse checks the train buff again, so the aura should stop when he dies
(death clears buffs, section 5). A sound on the start of a train is gated by its own 600-tick buff.

**A debuff that must not stack (league_amumu's Curse).** Same-name buffs add up (section 5), so a
3 s `damaged_amplify` on every hit would reach +30%. Re-apply it from a pulse with a duration equal
to the period (60 ticks every 60): one instance while the enemy stays in range, gone a second after
it leaves. The ult's longer curse adds a caster "window" buff that the pulses check to skip theirs.

**Pull yourself to the first champion hit (league_amumu Q).** `LinearProjectile {penetrate: false,
applied_target: EnemyChampion}` passes minions and monsters (the AI cannot aim around them); its
`applied_effects` hold the damage, `Stun`, `MoveToTarget` (the Lee Sin Q2 dash, without the delay)
and `CasterAnimation` for the flight. A miss moves nothing.

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
change either.

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

Where the damage comes a tick later than the hit (league_jinx R: the blast is a `RangeProjectile` with
`delay: 1` in the rocket's `end_effects`), add the casted effect from a `Delayed {tick: 2}` and read the
flag at tick 7, or it runs before the blast and clears the flag. In 10 simulated games every basic-attack
kill (13) and every rocket kill of the champion it struck (3) was found, and no other hit set it off.
Rejected on the way: a `RandomTarget` from the hit point after the damage (the dying unit is still
valid that tick), a `Delayed` effect on the target (it runs on the dead), and one twin for all targets
(a minion dying next to an enemy champion set it off). A splash hitting two champions shares one flag,
so a survivor's check can hide the other's death. The same check could build other takedown effects
(Darius's Noxian Guillotine reset).

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
the trap is a chain of short links, each started where the thrown `ParabolicProjectile` landed:
- a `ViewEffect` of the lying trap for the link's length (15 ticks);
- a `RangeProjectile` with `delay` 14 and `apply` 1 on `EnemyChampion` (it checks on the link's first
  tick, section 4), whose effects (skipped under a lock) bite:
  `Bind`, damage, a `ViewEffect` on the victim, and `WithSelf {Delayed {tick: 1, AddCasterBuff lock}}`,
  so every champion inside at that check is bitten before the lock falls;
- a hidden `ParabolicProjectile` of `travel_time` 15 aimed at the same spot, whose `end_effects` start
  the next link unless the lock is on.

The first link only arms (no check). 20 links make 5 s; after a bite the next link never starts, so the
trap vanishes a tick after it snaps. The lock lives on the caster and is shorter than the cooldown, so
it never blocks the next throw. In simulation 77 throws: 46 bit a champion, 31 ran out.

**A trap that lasts, with three at once (league_teemo Noxious Trap).** league_jinx E's links are
projectiles nested in each other's `end_effects`: its file is 119 levels deep, and serde_json stops at
128, so that chain cannot run much past its 20 links (5 s). A `Position` cast keeps its cast point for
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
is a `Delayed` of 240 - 20k + 2 ticks, landing 2-22 ticks after the return, and checks a caster buff that
outlives the spirit by 32 ticks (no pops once he died). The mark on the enemy is an `AddBuff` on the target
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
does spawn (nine levels here). Her death stops the pulses (a dead caster fires no projectile). Until 0.25.0's review
a single `Delayed {tick: 180}` `RangeEffect` (70000) stunned every enemy champion near her then, also one that had
run off and come back or had never been chained (the user: "脱离了大招的线就不应该眩晕了吧"). In 16 simulated games
62 champions were chained: about 36 died within the 3 s, 12-19 ran out of reach and 0-3 were stunned, at check
ranges of 60000 to 105000 alike - a champion walks about 1.2 cast radii a second here, against 0.56 in League.

## 8. Gotchas

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
- A buff's view can outlive its unit: Garen died mid-spin and the whirl of his 3 s caster buff
  stayed on the body (no view_buffs option covers death). For a purely visual timed effect,
  play `CasterViewEffect` on a timer instead (one per `Delayed` pulse, `is_follow: true` in
  `view_effects`); keep buff views for states that must vanish on consumption (Q ready).
- Run `python scripts/lint_mod.py <mod>` after every edit.

## 9. Checking a fact against the engine

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
