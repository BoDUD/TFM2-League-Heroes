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

## What is done with it

- 2026-11-08 `league_peel` 0.1.0: the support and nearby top / jungle hit whoever dives our ADC, and its log records
  what the game's AI had them doing when the dive started (does the game peel by itself?). Measured with
  `league_fight_log` (dives, help, ADC deaths) against a launch without it.
- Next candidates: a native hook that turns the decision trace on; the 0.7 tactic choice and FOCUS-SEL; calmer laning
  (25 kills before 10:00 in the 2026-11-07 logs); kiting.
