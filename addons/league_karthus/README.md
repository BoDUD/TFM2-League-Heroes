# 卡尔萨斯附加包（测试版 v0.4.0）

主包 `league` 保持纯数据。用户选了「被动做附加包」。这个附加包用原生代码做主包数据做不到的**死亡契约**：

- 英雄联盟里卡尔萨斯死后化成灵体，7 秒内免费放技能，然后才倒下；灵体**选不中、不受伤害、免控，不能走动、不能普攻**。
  数据读不到血量，主包做不了。
  附加包的被动 `league_karthus:death_defied` 每 10 tick 给他挂一个 30 tick 的不死 buff `league_karthus_p_guard`，
  这样致命伤害只会把他打到 1 血。他到 1 血（并且身上没有别人给的不死，比如基兰的大招）时就**化成灵体** `p_t` tick（420 = 7 秒）：
  - 先放逐自己 `FLUSH_T`（12）tick：游戏里只有放逐让单位选不中，正在打他、追他的英雄、小兵、塔都丢了目标；
  - 之后隐身（`entity_set_invisible`，每 30 tick 续一次：远处的敌人看不见他）；
  - 敌方英雄的普攻、技能点向灵体时，挂在每个英雄上的钩子 `league_karthus:shun` 把它改到别的目标上（见下）；
  - 不再受伤（`damaged_reduce` 100%）、放逐结束后免控（`league_karthus_p_ward`）、不能走动（移速 -100%）；
  - 身上挂 `league_karthus_p_spirit`（附加包的副本里绑了灵体的画面），播灵体音效和台词。

  - **敌人选不中灵体**（0.4.0，用户 2026-11-02：「死歌死亡后感觉有点不对 不能像塞恩那样吧 应该和英雄联盟一样吧？现在死歌死了后别人
    还在攻击灵体 英雄联盟里不是灵体吧」）：0.3.1 的灵体只是隐身，可游戏的隐身只挡远处的视野，贴着他的敌人照样看得见、选得中
    （tfm2-hero-mod 的 champion-data「Invisible is not untargetable」），1 血的灵体又正是游戏的 AI 最想补的目标：那晚的 46 个灵体
    一直挨打。真正选不中只有放逐，可放逐也拦着他自己出手、遮住他队伍在他身边的视野，所以只在化成灵体时放逐一下，之后由钩子
    `league_karthus:shun`（优先级 200000：在所有挑目标的钩子之后，在蕾娜塔的狂暴和解锁总闸之前）管：敌方英雄的普攻、技能
    点向灵体时，改成同一格点向它 90000 内看得见的别的敌方英雄（普攻还可以是小兵、召唤物，不打塔），近的先；都不行就退出
    亵渎的圈（离灵体 70000）、再远就原地站着。小兵和塔没有 AI 钩子：放逐让它们丢了目标，之后贴着灵体的还可能再打它（不掉血），
    倒下时的日志会数出来。
  - **灵体站着放技能**（0.4.0，英雄联盟的灵体不能走动、不能普攻）：游戏的 AI 看他 1 血就逃跑或回城，灵体 7 秒白白浪费。本包的
    AI 钩子 `league_karthus:spirit_ai`（优先级 105，在 league_ult_press 之后）在灵体期间按：R（值得时，全图，近的英雄先）>
    E（没开着：55000 内的英雄，没有就小兵、野怪）> Q（80000 内的英雄，没有就小兵、野怪）> 立痛苦之墙的普攻（墙好了、普攻
    够得着的英雄：W 在普攻里）；只挑他的队伍看得见的目标（0.3.1 的日志里灵体对着射程里的英雄按了几十到上百 tick 的 Q 放不出来，
    那时目标多半在草里）。都没得放就原地站着，游戏的 AI 想逃、想回城、想普攻都换成站着。一招按下去，游戏的 AI 没下新命令时隔
    4 tick 才再按（0.3.1 每 tick 都按）；同一招按了 30 tick 还没放出来，记 `SPIRIT PRESS STUCK`，这个目标 60 tick 内不再挑。
    0.3.1 为查这件事而现形 20 tick 的自诊断去掉了：现形时谁都能打他。
  - **安魂曲挑时机**（0.3.0，用户 2026-11-01：「最好改成死后放大 或者复活后在泉水放大 放大也要看敌方血量吧？不能乱放吧」
    「灵体状态下放大是不能被打断的」）：按他现在的法强和每个敌方英雄的生命 + 护盾、魔抗算出 R 打完剩多少血
    （200 + 75% 法强，魔抗按 100 / (100 + 魔抗) 打折），只在两种时候放：
    - **灵体里**：能打死一个、或把一个打到最大生命 30% 以下；
    - **泉水里**（开局和每次复活时记下的出生点 25000 以内，复活后、回城后都算）：能打死一个、或把两个以上打到 20% 以下，先打剩血最少的；
    - 别的时候游戏的 AI 想放就拦下，改成 Q、E、打 70000 内的敌方英雄，都不行就照它上一次的走路命令走（日志 `R HELD`、`R FOUNTAIN`）。
    灵体时开始的引导不会被控制打断（主包数据的打断检查看到 `league_karthus_p_spirit` 就跳过），灵体时间到了引导还没完就等它放完再倒下
    （`SPIRIT HOLDS`）。大招的说明后面加了「只在灵体里或泉水里、敌方英雄残血时放」。

  时间到灵体倒下：按固定伤害记在最后打他（化成灵体之前）的人头上。每条命都有（英雄联盟每次死亡都会触发）。
  只有这条命里见过他 1 血以上之后，1 血才算致命伤（赛恩附加包的教训：游戏 0.6.4 开局第 0 tick 读到的血量是 0）。

- **亵渎的圈**（主包 0.297.0，用户 2026-11-02：「还有E的范围要做大点啊 现在太小了吧 死歌的圈」）：E 的圈是英雄联盟的 550 码
  （`e_r` 55000，原来 30000），圈里有敌人就开（`e_cast` 55000）；圈的画面由 `tools/art/import_karthus_fx.py` 按 `e_r` 重画。

数字：被动的参数写在英雄数据的 `passive.params`（`{"p_t": 420}`），由 `make_override.py` 从 `tools/kit/build_karthus.py`
的参数表 `P` 写入；`GUARD_T`、`GUARD_EVERY`、`HIDE_EVERY`、`FLUSH_T` 和钩子的距离写在 `src/lib.rs`，单元测试核对参数表
（`q_range`、`e_cast`、`e_r`、`w_r`、`atk_range`、`r_dmg`、`r_ratio`、`r_ch`）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.297 以上：亵渎的大圈画在主包里）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_karthus` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_karthus.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看卡尔萨斯的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Karthus (player 0, team 0), ...`：出生；
   - `SPIRIT #1: lethal damage caught at 1 hp (last hit by ...), a spirit for 420 ticks, banished 12 ticks first`：化成灵体
     （行尾有 `(entity_banish refused)` 就是放逐没成，告诉我）；
   - `SHUN #1: Attack on the spirit league_karthus#20 -> Attack on league_ahri#22`：敌方英雄要打灵体，改打别人
     （`-> out of Defile` 退出亵渎的圈，`-> a stand` 原地站着）；
   - `SPIRIT AI #1: Skill on ... (the game's AI: Move)`：灵体时钩子替 AI 放了技能（立墙的普攻记成 Attack）；
     `SPIRIT PRESS STUCK #1: ...`：同一招按了 30 tick 没放出来；
   - `SPIRIT HIT #1: struck by ...`：灵体还是挨了打（谁打的）；
   - `SPIRIT KILL #1: ... killed by the spirit`：灵体击杀了英雄；
   - `FALL #1: the spirit's time is up, killed by ...; struck as a spirit by champions 0 times, minions 0, towers 0, others 0`：
     灵体倒下，这次灵体挨了谁几下（英雄那一项应该是 0）。

## 开发

- `python addons/league_karthus/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的卡尔萨斯和参数表一致）。
  主包的卡尔萨斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_karthus`：单元测试（别人给的不死、隐身续期、参数、和参数表一致、灵体挑什么招、
  拦下 R 时改按什么、敌人退出亵渎的圈、钩子的先后、挨打的计数）。
- 在 `addons/` 下 `cargo build --release -p league_karthus`（Windows）得到 `target/release/league_karthus.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
