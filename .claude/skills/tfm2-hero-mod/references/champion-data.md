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
- Self-buffs that should fire "in combat" work best as `casting_type: None` +
  `casting_target: EnemyChampion` + a `range` (cast when an enemy champion is that close) - this
  is how Nocturne's shroud is wired. `AllyOnlySelf` + range 0 also exists (Aatrox ult).
- `action_name` may be any tag: `ult_cast`, `skill2_dash`... Base uses this heavily.
- `can_use_with_move` lets the unit cast without stopping. No base skill uses it (LoL Reborn
  does), and it does not let the unit walk during a `CasterAnimation`.
- `patch_type_name` only appears in base data (patch notes); skip it.

## 4. Effect catalogue

Every effect is `{"type": "<Type>", ...fields}`. Counts = uses across base + 52 pack champions.

**Flow**
| Type | Fields | Meaning |
|---|---|---|
| Combine | effects[] | run all, in order |
| Delayed | tick, effects[] | run after `tick` |
| WithSelf | effects[] | apply to the caster *(inferred)* |
| SwitchByBuff | buff_name, effect_buff, effect_none | branch on whether the **caster** has the buff |
| SwitchByLevel3 | effect_start, effect_level3 | level-based branch, seen once *(semantics unverified)* |
| RandomTarget | range, casting_target, from_projectile, effects[] | pick a random valid unit in range, apply effects to it |
| RangeEffect | shape, target, apply_type:"AroundCaster", effects[] | instant area around the caster |

**Damage and sustain**
| Type | Fields | Meaning |
|---|---|---|
| Attack | damage, attack_ratio, hp_ratio, target_hp_ratio, attack_effect_type:"Target" | physical: damage + ratio% AD (+% max-HP parts) |
| ApAttack | damage, attack_ratio, hp_ratio, can_crit | magic: damage + attack_ratio% **AP** |
| FixedAttack | damage, attack_ratio, hp_ratio, target_hp_ratio | true damage: damage + ratio% AD + hp_ratio% of the caster's and target_hp_ratio% of the target's **max** health |
| Heal | amount, attack_ratio, ap_ratio, heal_type: Caster\|Ally\|Any\|AllyAll | heal (`Caster` heals the caster even inside a projectile that hit an enemy; `Ally` the allied target). No field scales with the target's missing health |
| Shield | amount, attack_ratio, ap_ratio, tick | shield for `tick` |
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

`AddCasted` never refreshes or replaces: `AddCastedEffect::apply` pushes a new entry on the target's
list of casted effects each time, so repeated hits stack, each with its own timer, and nothing caps
the count. `Bleed` is the base Inquisitor's bleed (league_darius uses it for Hemorrhage).

`attack_effect_type` on the three attack effects: `Target` (every pack writes it) hits the
effect's own target with no team check, so `WithSelf` + `FixedAttack` damages the caster;
the engine's other kinds are `EnemyTarget` (skips the caster's team) and `EnemyAll {..}`.
`FixedAttack` with only `target_hp_ratio` has an expected damage of 0 for the AI (it is
estimated from the caster's stats), which keeps a health cost out of the skill's score.

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

No effect and no buff field blocks, reflects or destroys a projectile (a wall like Yasuo W or Braum E
cannot exist); `ShrinkingBarrier` is a closing ring that hits units at its edge.

**Buffs** - `AddBuff {buff_state}` (on target), `AddCasterBuff {buff_state, only_to_enemy}`
(on caster), `RemoveCasterBuff {name}`. See section 5.

**Crowd control / states** (durations in ticks)
`Stun {duration}`, `Airborne {duration}`, `Bind {duration}` (root), `Taunt {duration}`,
`Banish {duration, end_effect_name?, lock_effect_name?}` (removed from play),
`Charm {tick}`, `Fear {tick}`, `Knockback {speed, tick}`, `Pull {speed, tick}`, `Grab {speed, tick}`,
`BlockAttack {tick}` (disarm), `BlockSkill {tick}` (silence), `BlockMoveSkill {tick}` (no dashes),
`Invisible {tick}` (target cannot be seen/targeted - Nocturne ult applies it to allies),
`CasterInvisible {tick}` (base Nightmare).

**Pull vs Grab** *(read from the SDK's game_core, `Entity::pull` / `Entity::grab`)*. Both move the
target in a straight line at `speed` units per tick for their duration (tenacity shortens it) and
are blocked by `cc_immune`. `Pull {speed, tick}` heads for the caster, or for the projectile's
position when it runs in a projectile's `applied_effects` (the Touhou Patchouli vortex), and does not
stop there: a target closer than speed x tick is pulled through and out the other side. `Grab
{speed, tick?}` always heads for the caster; with `tick` left out its duration is distance / speed,
so the target stops at the caster wherever it started (league_darius E).

**Movement**
| Type | Fields | Meaning |
|---|---|---|
| MoveTo | speed, range, end_effects[] | dash in cast direction/position, then end_effects |
| MoveToTarget | speed, range, end_effects[] | dash onto the target, then end_effects |
| MoveBack | speed, tick | hop backwards |
| RushTime | speed, tick, range, casting_target, penetrate, applied_effects[] | charge for `tick`, hitting units passed |
| RushMoveToBack | speed, applied_effects[] | dash through the target to 15000 units behind it, then applied_effects on it |
| DirTeleport | moved | blink `moved` units in the cast direction |
| Teleport | - | put the caster on the target's (or the cast point's) position |

*(read from the SDK's game_core)* `RushMoveToBack` aims at a point 15000 units (a fixed value) past
the target on the line from the caster, clamped to the map, and schedules `applied_effects` (plain
effects, no `casting_type` wrappers) on the target for when it arrives: a dash *through* an enemy
(LoL Reborn Fizz Q, Touhou Sakuya, league_yasuo E), where `MoveToTarget` stops on it. `Teleport` copies
the target unit's coordinates (`Targeting`) or the cast point (`Position`) onto the caster and does
nothing for `Direction`. `Airborne` on a unit that is already airborne keeps the longer of the two
remaining times; every CC's duration is cut by the target's `toughness` (x (100 - toughness) / 100),
and airborne also cancels the target's dash.

**Projectiles and zones** (all take `name` -> bound in `view_projectiles`; `applied_effects` items are `{"casting_type": "Targeting", "effect": {...}}`)
| Type | Extra fields | Meaning |
|---|---|---|
| TargetProjectile | speed, y_offset, applied_target | homing on the target |
| AutoTargetProjectile | speed, range | seeks targets itself |
| TargetSplashProjectile | speed, range, y_offset | homing, then splash |
| LinearProjectile | speed, range, shape, penetrate, end_effects, y_offset | skillshot |
| BackToCasterLinearProjectile | speed, range, shape, penetrate, end_effects | boomerang |
| ParabolicProjectile | travel_time, range, shape, range_effect_name, end_effects | lobbed to a spot |
| LineRangeProjectile | width, length, delay, apply | line/rectangle telegraph, hits after `delay` |
| RangeProjectile | shape, delay, apply, end_effects | circle at target spot after `delay` |
| RangePeriodProjectile | shape, tick, period, first_delay, end_effects | persistent zone ticking every `period` |
| ApplyInProjectile | shape, tick, follow_caster | aura / zone that can follow the caster |

`applied_target`: `Enemy`, `EnemyWithoutTower`, `EnemyChampion`, `EnemyChampionInCC`, `Ally`,
`AllyChampion`. RangeEffect `target` also accepts `AllyOnlySelf`, `AllyNotSelf`.
`ApplyInProjectile` has no `period` and `RangePeriodProjectile` no `follow_caster` (SDK), so an aura
that ticks while it follows the hero is built from `Delayed` pulses of a `RangeEffect` around the
caster (section 7, "Aura that runs while he fights").

Shapes *(`ProjectileShape::is_in` in the SDK's game_core; every radius and half-size also counts the
collision radius of the unit tested, and for RangeEffect the caster's too)*:
- `{"Circle": {"radius": N}}`
- `{"Rect": {"width": W, "height": H}}` - axis-aligned around the centre, never turned
- `{"Line": {"width", "from_x", "from_y", "to_x", "to_y"}}` - a segment with fixed coordinates
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
holds). Some pack buffs omit it - set it explicitly.

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
- `z` < 0 draws under units (ground decals, zones); `is_follow` makes an effect follow its unit.
- The whole schema (serde names in the SDK's `game_core` metadata): `view_effects` are `Animation` or
  `LoopAnimation`, each `{name, anim, tag, z, is_follow}`; `view_projectiles` are `Animated
  {repeat}`, `Sprite` or `ThreePhase {pre_tag, loop_tag, remove_tag}`. There is no rotation or flip
  field: how a view is placed depends on what plays it.
- A projectile's view is turned to its direction (a `LineRangeProjectile` rectangle: drawn pointing
  right, see "Cone / fan"), so cast upward it lies across the screen and cast left it is upside down.
  A `CasterViewEffect` is not turned: it is drawn at the caster's pivot, mirrored when the caster
  faces left (the base gunner's backward-run dust is drawn only behind him), and stays where it was
  played unless `is_follow`. An `Animation` plays its tag once, so a view that must stand for
  seconds lists its loop frames again (a 4 s loop of 100 ms frames is 40 frames).
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

**Skill empowers the next attack.** The skill adds `x_ready` (Time buff); `attack` starts with
`SwitchByBuff x_ready` -> empowered effect + `RemoveCasterBuff x_ready`.

**Recast / charges.** `cooltime_use_count: N` on the action (base Nightmare fires 3 shards).
For different 1st/2nd casts, add a short `x_recast` buff on first cast and `SwitchByBuff` on it.

**Dash then hit.** `MoveTo` (direction) or `MoveToTarget` (unit) with `end_effects:
[ViewEffect, RangeEffect{Attack, Stun}]`. Add `CasterAnimation` with a dash tag for the travel.

**Telegraphed AoE.** `RangeProjectile {delay, apply}` / `LineRangeProjectile {width, length,
delay, apply}` / `ParabolicProjectile {travel_time}`; or `ViewEffect warning` + `Delayed {tick}
RangeEffect`. `apply` is how many ticks the area stays live after `delay`; each unit is hit once
(base spellbreaker Q: delay 8, apply 3, one hit per its tooltip).

**Cone / fan (Ashe W).** No projectile takes an angle, but `LineRangeProjectile` in a
`casting_type: Direction` action is a rectangle from the caster toward the target, and its view
sprite is centred on the rectangle and turned to the cast direction: drawn pointing right from
x = -length/2 to +length/2 (measured on LoL Reborn's Swain Q fan, Lux R and Jhin W sprites). So a
fan sprite with its apex at x = -length/2 starts at the caster. The hit area stays a rectangle;
draw the fan a little wider than `width` (oppi's Swain does). league_ashe W: width 45000, length
80000, delay 14, apply 3, 9 arrows over +-28 deg, 7 frames x 40 ms, view `repeat: false`.

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
line, charge, beam, fade), a second one with the same shape and a shorter `delay` deals the damage
(Touhou Marisa: visual delay 120; league_lux R: visual delay 55, damage delay 28, 240000 x 16000).
The view is drawn at the unit's pivot height and turned to the cast direction, so keep the beam
centred vertically in its canvas (an offset would flip when she fires to the left) *(inferred)*.

**Burn / poison.** `AddCasted {casted_type: Fire, duration, period, effects: [ApAttack]}`.

**Untargetable window.** `RangeEffect` on `AllyOnlySelf` applying `Invisible {tick}`, plus a
caster buff with `cc_immune` / `damaged_reduce` if needed.

**Channel with its own animation.** `CasterAnimation {name, tick}` + `Delayed` hits +
`RemoveCasterAnimation` at the end (Nocturne ult, Marisa laser).

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

**`MoveToTarget` needs a target.** It dashes to the action's target, so use it in `Targeting`
actions (Nocturne R, Gragas E). Under `casting_type: None` there is none and nothing moves (seen
in-game); LoL Reborn Jax Q wraps it in `RandomTarget {casting_target, range}` instead.

**Multi-hit on random enemies.** Several `Delayed` blocks each holding a `RandomTarget`.

**Projectiles at random enemies.** `RandomTarget {range, casting_target, effects:
[TargetProjectile]}` fires from the caster at the picked unit (LoL Reborn Ezreal E). A unit can be
picked more than once. league_ashe W started this way (one arrow at the target plus four random
ones); the user saw homing arrows, not League's cone, so it became the fan above.

**Dash to whoever the skillshot hit (league_leesin Q2).** A projectile's `applied_effects` run
with the hit unit as target, so a `MoveToTarget` there dashes the caster to it (LoL Reborn
Nautilus Q pulls itself in this way). Lee Sin wraps it in `Delayed {tick: 12}` (the mark shows
first) with `Sfx`, the dash and `CasterAnimation q2` inside; the dash's `end_effects` deal the
second hit. The action's `duration` covers wind-up, flight and delay (44 ticks). *(inferred
from the pack; not yet seen in-game)*

**Kick it back into the others (league_leesin R).** `Targeting` on an enemy champion: `Attack` and
`Knockback {speed: 3000, tick: 18}` on the target, plus a `LinearProjectile` toward it with
`penetrate: true` at the same speed (LoL Reborn Nautilus R knocks up along a line this way). The
projectile starts at the caster, a melee range behind the flying target, so it keeps that gap and
hits (`Airborne`, damage) only what the target flies past; its range stops the circle short of the
landing spot. *(inferred: Knockback pushes away from the caster at a constant speed)*

**Heal an ally at a health cost (league_soraka W).** `Targeting` + `AllyNotSelf`: `Heal
{heal_type: Ally}` on the target, then a 3-tick caster buff with `undying: true` and
`WithSelf {FixedAttack {damage: 0, target_hp_ratio: 6, attack_effect_type: Target}}` - 6% of her
own max health that can never kill her (League forbids the cast below 5% health). Under
Rejuvenation the cost is skipped and the target gets Rejuvenation too, as in League. *(inferred
from the engine code; not yet seen in game)*

**Heal over time (league_soraka Rejuvenation).** `AddCasted {casted_type: Heal, duration: 150,
period: 30, effects: [Heal {amount: 15, ap_ratio: 6, heal_type: Ally}]}` on the target heals it
5 times (75 + 30% AP over 2.5 s); for the caster itself wrap it in `WithSelf` with `heal_type:
Caster`. Every cast adds another instance. *(seen in the SDK simulation: the caster's heal and
self-heal statistics rose with it; not yet seen in game)*

**What a heal is worth to the AI.** Heals score `min(heal, missing health)` (section 3), and the
statistics count only what landed. In simulation a bigger flat heal on league_soraka W (180 ->
320) healed no more in total; a longer range (60000 -> 90000), a shorter cooldown (5 s -> 4 s) and
Rejuvenation passed to the target did (+50% in 10 simulated minutes, near base Priest).

**Heal every allied champion (league_soraka R).** `Targeting` + `AllyChampion` with range 960000
(base Priest's ult range) and `RangeEffect {radius: 960000, target: AllyChampion}` around the
caster. Cast as `None` on `AllyOnlySelf` (Touhou Reimu, LoL Reborn Alistar) the AI fires it as soon
as it is ready, full health or not; a target lets the heal score above (0 at full health) decide.

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
*(inferred: death clears buffs)*. A sound on the start of a train is gated by its own 600-tick buff.

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
(12 s) and `WithSelf {Shield}` (a `Shield` in a `Targeting` action would shield the enemy). The first
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

## 8. Gotchas

- `action_name` / `CasterAnimation.name` must be real sprite tags. Two LoL Reborn heroes use
  `action_name: "skill"` while their sprites only have `skill1`.
- `SwitchByBuff` checks the caster; the buff must be added somewhere in the same kit.
- Keep `start_timing <= duration`; long channels need a long `duration` (or `Delayed` effects).
- Use namespaced names for every buff/projectile/effect (`league_garen_*`) - names are global-ish
  and collisions with other mods are hard to debug.
- Custom sounds must be injected with override entries or `Sfx` will not find them
  (see `text-audio.md`).
- The engine plays `<champion id>_attack` on every basic attack by itself; never play that name
  from the effect tree too (see `text-audio.md`).
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
