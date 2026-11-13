# The game's own match AI (reverse-engineered)

Read from the game build of 2026-11-04 (`TeamfightManager2.exe`, 94,043,136 bytes) with `tools/re/ai/re_ai.py`
(user 2026-11-08: 「我得到授权了 你可以直接逆向整个AI的逻辑来改善」). Addresses below are RVAs of that build; they move with
every game update, the names and the structure much less.

## Where it is

- The EXE is a stripped Rust build. Crates: `game-ai` (the match AI), `game-core` (simulation, banpick, transfers),
  `game-view`, `engine-*`. Every panic site keeps a `core::panic::Location` (file, line) in `.rdata`, so
  `re_ai.py index` maps functions to the 193 `game-ai\src\...` files they panic from (885 functions; the big ones:
  `plan\handler.rs` 78 KB, `big_plan\battle.rs` 4,600+ lines, `big_plan\fight_model.rs`, `fight_check.rs`, `rl.rs`).
- The classic mod SDK 0.5.1 shipped `game_core` as an rlib **with symbols**: its
  `simulation::state::player::aos_ver_hamster::plan_legacy` is the ancestor of `game-ai` (same plan and sub-plan names),
  so `re_ai.py syms051` lists real function names (`old::battle::select_tactic`, `resolve_fight`, `check_initiating`,
  `tower_dive_is_viable`, `expected_trade_net_hp`, `v21_should_defer_support_target`, `combat::model::assess_fight`,
  `death_battle::judge_focus`, `team_shared_focus`, `goal_data::get_die_tick_player`, ...) and `re_ai.py rlib <name>`
  disassembles one with its calls named.
- Format strings are length-prefixed templates (the `lea` points at the length byte): `re_ai.py str` / `fmt`.

## The layers (each player, every tick)

| layer | files | what it decides |
|---|---|---|
| team plan | `plan\team_plan.rs` + `audit`, `cascade`, `gank_gates`, `obj_contest`, `objective_discipline`, `objective_handlers`, `objective_helpers`, `opportunities` | the team's objective (lanes, Morgard = Baron "epic", Serpen = dragon, sieges, nexus), commits (`OBJCOMMIT` take / gather / cut / stall), first dragon (`FIRSTSERPEN`), sieges (`SIEGE open / release`), defence departures (`DEFDEPART`) |
| handler | `plan\handler.rs` + `handler\assign`, `auction`, `engage`, `lane_ops`, `obs`, `relays`, `scene_feedback`, `signal`, `modes` | each player's big plan, ganks / joins / invades (`TRAIT_AUD`, `[GANK_END]`), tower binary (`TWBIN` flip / harvest / drop), scenes (`SCENE-CONTINUE`), focus picks (`BUFFPICK`, `TBPICK`, `TBHOLD-PICK`) |
| big plan | `plan\big_plan\*` | Force, PassiveLine, PassiveJungle, SinglePlanLine, SinglePlanBattle, Battle, DeathMatchBattle, LineGanker, EpicHuntAndPoke, SerpenHuntAndPoke, ActiveRecall, AttackNexus, DefenseNexus |
| sub plan | `plan\sub_plan\*` | LineDefense, LineSafe, LineWait, Recall, Hide, Jungle, Battle, DeathBattle, EpicCheck / Hunt / Poke, SerpenCheck / Hunt / Poke, AttackNexus, DefenseNexus, ObjContest (+ `act_gates`, `battle_common`) |
| small action | `small_action\around`, `cast`, `lane_minion`, `move_actions`, `trace` | Idle, Attack (target), Around (region / position / bush: Stand, Hold, Reposition, LastStand), Trace (focus, Kiting, KitingBack, RunAway, End), Dodge, Skill / Skill2 / Ult, Stop, Recall |

A battle plan carries `main_goal`, `sub_goal`, `signals`, `support_target`, `with_dive`, `dive_tower`, `help_called`,
`well_runaway`, `main_objective`, a stance (Commit / Reposition / HoldForSpawn; Stand / Hold / LastStand / Disengage)
and a **tactic**: Standard, Frontline, Backline, DPS, Skill, Burst, Peel, AllIn. In 0.5.1 `select_tactic` was:
Standard for the first 85 ticks, Frontline for style 0, DPS when the burst / sustained damage ratio is under 30,
Backline for style 2, else Standard (Peel / Burst / AllIn chosen elsewhere). The 0.7 version is not located yet.

Fights are judged by time-to-die models: `big_plan\fight_model.rs`, `fight_check.rs` (`FIGHTDIR` prints die / fdie /
na / ne / can / model), `position_eval.rs`, `action_score.rs`, `score_parameter.rs`, `hit_window.rs`, `buff_value.rs`,
`finish_race.rs`, `game_finish.rs`, `tower_discipline.rs`, `minion_wave_risk.rs`, `turnback.rs`, `deploy_stance.rs`.

## Its decision trace (off)

About 114 places build a line with `format!` and push (label, text, tick) through fn `0x161d880` into a `Vec` at +0x48
of a recorder. Each place first checks a byte at +0x3b behind the AI context's second pointer (in the battle plan's
update the context is the 5th argument: `[ctx]` = sim with the tick at +0x1b8, `[ctx+8]` = the flags); the serialized
AI state names it `trace_on` (next to `trace_tick`, `trace_changes`, feature flags `mf_obj_clear`, `comeback_pick`,
`fs_pairing`, `seo_cover_pick`, `seo_serpen_punish_issues` and many `audit_*` counters). Nothing in a release game turns
it on; a native hook that sets it and copies the lines to a log would show every decision with its reasons.

Some lines (`re_ai.py fmt`):

- `FOCUS-SEL T.. tick= .. -> .. ne= pool= prev_in_pool= indiv= sup= team=` (focus target: own pick, the support's, the team's)
- `[TANKAVAIL] T.. tick= die= avail= held=`, `[TBFLEE] T.. focus= sub=`
- `BRACE T.. tick= die= escape= sub= -> KitingBack`
- `DIVE T.. holder= secured= entry= die= mdt_tw= focdt= tgt_hp= nA= nE=`, `DIVE-ABORT` (uncatchable / personal die /
  resolver Disengage), `DIVE-HOLD`, `SOAK`
- `FIGHTDIR T.. tick= sub= dir= die= fdie= na= ne= can= model=`, `STANCE-DIE`, `JOINGATE`, `SCENE-FOCUS`, `WAVE-FIRE`
- `line backfight support: line .., ally .., focus ..`

Environment switches read once (printed with `eprintln!`): `SHOP_TRACE`, `SUPFR_TRACE`, `GK_VIABLE_TRACE`,
`LANE_RECALL_TRACE`, `TFM2_LOWBY_TRACE`; `NT_TRACE`, `DM_NO_DODGE` in game-core / death match.

## Neural networks: not in 5v5 fights

- `rl.rs` parses an asset of type `rlp`: `asset/base/setting/death_match/ai_policy` (151,855 bytes, a text header with
  ent_dim, proj_dim, game_dim, cand_dim, n_ent, n_proj, n_glob, n_head: attention over entities and projectiles that
  scores candidate actions). Only the death-match mode uses it.
- `network` assets (`base_network`, `death_match/base_network`, `single_lane/base_network`) and the `item_network`
  `base_item_network` serve banpick (`LogisticSGDAgent`), items and the transfer planner. `macro_weights` is the asset
  `lol_macro` overrides.
- The 5v5 match AI is hand-written rules: it can be read, and changed where a lever reaches.

## Levers

1. `StablePlayerAi` (mod API): every tick a hook sees the game AI's input for one player and may replace it
   (league_macro after Baron / at the nexus, league_peel, the hero add-ons). Survives game updates.
2. `strategy_get_json` / `strategy_set_json`: the team tactic document (智能BP).
3. Assets through `mod.override_info` (`macro_weights`, settings).
4. Native hooks from league.dll (`game_places`: byte patterns, `.pdata` bounds, a stub like `league_main/src/cache.rs`):
   reaches anything (the decision trace, a plan's choices), breaks more easily on game updates.

## Key places (2026-11-04 build)

| RVA | what |
|---|---|
| `0xe3a040` | handler update (78 KB; PLANEND, TWBIN, RECVPICK, JOINTRG, TRAIT_AUD) |
| `0xec8b10` | big-plan dispatch (jump table, calls each plan's update) |
| `0xee1810` → `0xed1610` | Battle plan update (29.5 KB; FOCUS-SEL at `0xed59b6`, TANKAVAIL; trace gate `cmp byte [rax+0x3b], 0` at `0xed582b`) |
| `0xed93f0` | BRACE -> KitingBack |
| `0xedbe40` | dive checks (DIVE-ABORT) |
| `0x107a7e0`, `0x10a0c70` | sub-plan battle (`sub_plan\battle.rs`) |
| `0xf60250` | fight model (38 KB) |
| `0xf93e00` | fight check (12 KB) |
| `0x161d880` | the trace recorder push (114 callers) |
| `0xfb57e0` | rl.rs `rlp` header parser; loader `0x9b7df0`, registered as type `rlp` in `0xccd3e0` |

## Game 0.7.2 (2026-11-11): how the AI estimates a kit

Read while looking for why the 0.7.2 AI hardly ever orders Kai'Sa (and Draven, Samira, Graves) to attack champions (the
user: 「卡莎是真有点问题」「也不平A」). The cause was **not** found here - for her these estimates come out like any other
marksman's - but this is what the AI reads from a hero's data, with the RVAs of the 0.7.2 EXE (94,603,776 bytes;
`re_ai.py --work <dir> index` again for every new EXE, then `tools/re/ai/effect_types.py --work <dir>`).

- **Effects are trait objects.** The data's `DataEffectDef::X` becomes a runtime `XEffect` struct behind an `EffectType`
  vtable (167 types, 285 vtables; `effect_types.py` lists them by the name their +0x18 method writes). The slots the AI
  calls:

  | slot | what | notes |
  |---|---|---|
  | `+0x30` | expected damage (AD, AP) | `AttackEffect`: damage + ratios x the caster's stats; `CombineEffect` / `DelayedEffect` / `WithSelfEffect` / `RandomTargetEffect` / `MoveTo*` / the projectiles: the sum of their children; `SwitchByBuffEffect`: the branch the caster's **current** buffs pick; `HealEffect`, `ShieldEffect`, `AddBuff*`, every CC, `CasterInvisibleEffect`: 0 |
  | `+0x38` | the same against one target, as an Option | a container sums `+0x38` where a child answers and `+0x30` where it does not (helper `0x1a97390`) |
  | `+0x58` | percent of the target's health | callers add target hp x it / 100 |
  | `+0x60` | expected damage against one target | what the DPS estimate calls on an action's effect |
  | `+0xb8` | expected CC time (Option) | `StunEffect`, `BindEffect`, `AirborneEffect`, `BlockAttackEffect`, ... return their duration; containers forward |
  | `+0x240` | a mask | 0 for most; **0xff for `CasterInvisibleEffect` and `ModEffect`** (a mod's `Native` effect), 2 / 4 / 8 for a few base ults; containers OR their children (a `SwitchByBuffEffect` both branches). Non-zero: the kit ledger does not cache the action |

  A mod's native effect is a `ModEffect`: its `+0x30` asks the mod (`StableEffectType::expected_damage`, `expected_cc_time`,
  `expected_heal`, ... in the stable API - all default to nothing). A hero whose damage lives in a native effect or a
  native passive is worth 0 to these estimates unless the add-on answers.
- **DPS** `0x1039250(sim, entity, target)`: for the attack (`entity+0x488`), skill (`+0x4c0`) and skill2 (`+0x4f8`, when
  the hero has three actions) it takes `effect.+0x60(...)`, runs it through the damage formula against the target
  (`0x1e93a40`), x 100000 and divides by the action's interval (cooldown `+0x568` / `+0x578` / `+0x588` scaled by attack
  speed `+0x3f4` or haste `+0x3f8`). The ult is not in it. 0.5.1's `utils::dps_ratio` is the same sum (its `select_tactic`
  compared the attack's share of it with 30 %).
- **Who wins a duel** (`plan/handler/lane_ops.rs`, fn `0x10c57a0`): for me and an enemy laner, time to kill =
  hp (`+0x620`) x 100000 / the other's DPS on him; when I need longer to kill him than he needs to kill me a flag is set
  on the lane's verdict (bit 1). The same DPS is used by `passive_jungle.rs`, `free_dist.rs` and two small comparers
  (`0xf84020`, `0x1063f00`).
- **The fighter snapshot** `0x1850c50` (30 callers, almost all in `fight_check.rs`, one in `big_plan/battle.rs`): the
  four actions' intervals, the effective health, and per action a bit for "mask `+0x240` not 0", "`+0x238`" and the
  expected CC - what the time-to-die model starts from.
- **Kit ledger** (`kit_ledger.rs`, `0x10a6b90` / `0x10a6ff0` / `0x10a7550`): a per-tick cache of those estimates by
  (player 0-9, action 0-3, target 0-9) and a signature of level and buffs (`0x10b5d40`); an action whose mask is not 0 is
  never cached.
- **Tactics** are still `Standard, Frontline, Backline, DPS, Skill, Burst, Peel, AllIn` (the strings sit next to
  `Prep / Trade / Play / Trace` and `TryKill / Response`); where 0.7.2 picks one is not located.
- **Decision trace**: `decision_trace.rs` builds a record per player (`0x1162100`, 11.8 KB) when a byte at `+0x3c` of
  the flags behind the AI context (`[ctx+8]`) is set - the per-player update `0x1173810` tests it (in the 11-04 build
  the trace gate was `+0x3b`). `game-view/src/ui/decision_trace_card.rs` shows it in debug cards whose layouts ship in
  the bundle (`asset/base/ui/layout/debug_decision_card`: title, scene, objective, objective_why, plan, plan_why, sub,
  action, roster, verdict; `debug_fight_card`, `debug_scene_nav`, `debug_op_inspector`), all `visible: false`. What sets
  the byte in a release game was not found (no environment switch names it: `TFM_FRAME_PROFILE`, `TFM_UI_SCRIPT`,
  `TFM_PRINT_DEBUG_LOGS`, `TFM2_PLAN_THREADS`, `TFM2_LIMIT_CHAMPS`, `TFM_CONSOLE` are the ones there).
- **Hooks run from the lowest priority up**: league_ai_watch (-2,000,000) sees the game's own order, league_ult_press
  (100) presses after it - so the watch log's "attacks at champions" counts only the attacks the game's AI ordered.
- **What ruled Kai'Sa's data out**: her attack is `Combine[Sfx, TargetProjectile{Attack}, SwitchByBuff{... the E's
  buffs, CasterInvisible}]` - the estimate is one `Attack` like Varus's; her mask is 0xff, but so is Varus's (a `Native`
  in his attack) and the AI attacks with him. Stats, tags, category, ranges and the two data experiments
  (league_marks 0.1.5 / 0.1.6) made no difference. league_ult_press 0.6.5 works round it (a marksman the AI neglects
  pokes whoever stands in her own range).

## 2026-11-13: why the AI would not attack champions with some heroes

The Kai'Sa question above, answered from outside (league_ai_watch 0.3.0 counts the game's own attack orders per
champion; `tools/kit/range_buffs.py` has the numbers): an attack whose effect runs a `RangeEffect` on the caster or
on allies at cast time - the kits' "on me", a circle of radius 1000 round him - is hardly ever ordered at a
champion (30 of 37 such heroes under 1.75 a minute, ranged ones near 0; marksmen without one 4.5-7), unless the
attack's top `Combine` also holds league.dll's `league:range` (a `ModEffect` with `may_adjust_range`): all 7 heroes
with both attack normally, league_belveth with the same attack skeleton as league_aurelionsol among them. Moving
league_draven's automatic W from the cast under his projectile's hit brought him from 0.16 to 6.5 in game. Kai'Sa's
automatic E is such an area - her attack is not "one `Attack` like Varus's" to whatever reads it. The estimates
listed above (damage, DPS) are not what goes wrong: the neglected heroes' DPS came out like their neighbours'.
Which slot the AI reads there is still open: an area's size taken as the attack's reach would fit (ranged heroes
lost nearly every attack, melee ones part of them), and so would a query that a `ModEffect` in the tree answers
differently. The packers now add the node to every such attack (`range_buffs.reach()`); league_ult_press's
"neglected poke" stays until the logs show it is not needed.

## What is done with it

- 2026-11-08 `league_peel` 0.1.0: the support and nearby top / jungle hit whoever dives our ADC, and its log records
  what the game's AI had them doing when the dive started (does the game peel by itself?). Measured with
  `league_fight_log` (dives, help, ADC deaths) against a launch without it.
- Next candidates: a native hook that turns the decision trace on; the 0.7 tactic choice and FOCUS-SEL; calmer laning
  (25 kills before 10:00 in the 2026-11-07 logs); kiting.
