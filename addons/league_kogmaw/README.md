# 克格莫附加包（v0.1.0）

主包 `league` 保持纯数据。用户 2026-11-14 看了旧版被动的 GIF 说「大嘴死了还是看不到炸人啊」，然后「按英雄联盟改」。英雄联盟的艾卡西亚的惊喜：克格莫死后**身体本身**化成发光的虚空形态，4 秒里冲向敌人，碰到或时间到就爆炸，对周围的敌人造成真实伤害。主包是纯数据，数据里召唤物不会走，死了的英雄什么都放不出来，只能从尸体上飞出一颗追踪的小彗星（29 × 11 像素，速度 1000，游戏里飞 0.25 秒就到了，几乎看不见）。这个附加包用原生代码把他的身体做成一个真的单位：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 艾卡西亚的惊喜（被动） | 死后从尸体飞出一颗追踪小彗星，追向 70000 内随便一个敌方英雄，到了溅射 80 + 100% 攻击力真实伤害 | **他的身体化成虚空形态**（他自己的样子，深紫色、品红的光、亮色描边，和他一样大），每 tick 1000 冲向**最近的**敌方英雄，离它不到 12000 + 它的半径就爆炸，最多 4 秒（240 tick），时间到原地爆炸；对周围（12000 + 半径）每个敌人造成 80 + 100% 他死前攻击力的真实伤害，爆炸画面比旧的大得多、亮得多 |

## 怎么做的

- 副本（`override/`，`make_override.py` 从主包的 `league/champion/league_kogmaw.data_champion` 生成）：四个技能位里各有一份「看守」（每 6 tick 往他身上投一个看不见的抛物线弹，落地时他不在了就醒来），醒来时只有彗星和溅射那一支换成本包的原生效果 `league_kogmaw:void`；他倒下处的光 `p_wake` 和两个声音、看守本身、普攻、Q / W / E / R 一个字节不变（打包时 `tools/kit/attack_self.py` 给普攻加的那一层也一样：打包后的副本和打包后的主包只差这四处）。溅射的数（80 / 100% / 12000，速度 1000，找人范围 70000）写在 `src/lib.rs`，`make_override.py` 和单元测试核对主包，主包改了就停下。另外：挂上本包的被动 `league_kogmaw:life`，多一个画面 `league_kogmaw_p_void`（爆炸），普攻的说明换成本包的（被动那一句，五种语言）。
- 被动 `life`：他活着时每 tick 记下他的攻击力、队伍、生命上限、护甲、魔抗、位置。游戏里他一死英雄实体就没了（`champion()` 读不到，复活是新的实体），死后谁也读不到他的攻击力，所以先记下。
- `league_kogmaw:void`：在醒来的地方（他的身体）用稳定 mod API 的 `spawn_unit` 生成单位 `league_kogmaw_void`：生命、护甲、魔抗是他的，移速 1（引擎自己不挪它），攻击 0、射程 1（不打人），活 243 tick。召唤者先报他的旧实体号，宿主不收就报离得最近的活着的队友。
- 比赛钩子（死了的英雄的被动不跑，比赛钩子每份模拟每 tick 都跑）：单位读成站稳的单位（最大生命读出来）以后挂上护身 `league_kogmaw_void_guard`（受到的伤害 -100%、不死、穿墙）；之后每 tick 找最近的敌方英雄（活着、选得中），`entity_set_pos` 朝它挪 1000，挂 1 tick 的 `league_kogmaw_void_go`（正在走），清掉身上的控制、嘲讽到那个英雄（引擎自己的单位 AI 也朝它，朝向跟着走）。离它中心不到 12000 + 它的半径就爆炸，240 tick 到了也爆炸。宿主不让挪单位（`entity_set_pos` 不收）时把它的移速换成 1000（`entity_set_base_stat`），由引擎自己朝它嘲讽的那个英雄走（日志 `VOID WALK`）。
- 爆炸：12000 + 半径内每个敌人（不含防御塔、水晶、虚空形态）受到 80 + 100% 他死前攻击力的真实伤害（`deal_damage_typed` 真实伤害），先以他的名义（旧实体号），宿主不收再以形态的名义；爆炸画面、每个挨炸的人身上的 `p_hit`、`p_boom` 的声音；形态随后放逐到时间结束（API 没有让单位消失的接口）。
- 画面：单位的图 `league/champions/league_kogmaw_void`（`tools/art/unit_kogmaw_void.py`）是他自己的帧（待机、跑、攻击、挨打，1 倍和高清两套）改颜色：外圈描边亮粉紫，皮和骨头深紫 / 紫，背上的冠和亮边紫光，嘴、眼睛、嘴边品红到白热；待机身体不动只有光一闪一闪，死亡是碎成紫色火星。league.dll 按他的 PPU 1.794 画高清帧（`addons/league_main/src/hd.rs`）。爆炸 `league/effects/league_kogmaw_burst`（`tools/art/fx_kogmaw_burst.py`）用代码画，1 倍和 PPU 2 两套：白热的闪光、带凸起的品红光球和地上的环、紫色火舌、塌成黑色虚空，0.51 秒，最大 65 × 77（旧的 `p_boom` 25 × 45）。
- 显示钩子（`src/view.rs`，伊莉丝整身蜘蛛的做法）：显示世界里的形态身上有「正在走」时正在播的 idle 换成 run，站着时 run 换成 idle——引擎自己的单位 AI 只有 1 的移速，它画哪个不确定。
- 退路（什么都不丢）：宿主没有 `spawn_unit`、拒绝了、给的 id 5 tick 内读不成单位，或测试开关 `unit=off`——照主包放彗星：`spawn_projectile` 一颗 `p_form` 追向 70000 内最近的敌方英雄，到了由 `league_kogmaw:burst` 结算同样的溅射；宿主连彗星都不收，就直接在那个英雄身上炸。形态还没炸就没了，就在它最后站的地方炸。
- 每份模拟一个编号（`league_kogmaw_sim:<n>`，挂在两边的水晶上，水晶不收挂防御塔；league_eggs / league_karthus 的做法）：服务器并排跑的两份预演种子、实体号都一样，状态只按这些记会串。两边都选克格莫时各炸对面；同一次阵亡第二个看守弹落地不会再醒一次。
- 没做：英雄联盟里形态 4 秒内移速越来越快、玩家能操控方向；这里直线冲向最近的敌方英雄（不绕墙，穿墙），速度一直是主包彗星的 1000。形态选得中（API 没有「选不中」的接口；放逐会让它整个看不见），敌人可能会打它，但每下只掉 1 点、不会死。

## 在游戏里测

1. 主包（League of Legends Heroes 0.373 以上：要有 `league/champions/league_kogmaw_void` 和 `league/effects/league_kogmaw_burst`）要装着并启用，league.dll 也要是这个分支的（登记了形态的高清帧和爆炸的高清帧）。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_kogmaw` 文件夹放进 `<游戏目录>\mods\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看克格莫普攻的说明：开头是「【附加包】」，被动那一句是「死后化身虚空形态4秒……」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kogmaw.log`，每次启动游戏重写（上一次的留在 `.prev.log`），你看的那场每行都记，预演限了条数：
   - `VOID SPAWN`：他醒来（实体没了 / 复活躺着）、单位号、召唤者、他记下的攻击力和要打的伤害；
   - `VOID LOOK`：单位读回来的样子（种类、队伍、选不选得中、半径、生命、移速），护身挂上没有；
   - `VOID STEP`：每 15 tick 一行：追了几 tick、在哪、离他倒下处多远、追的是谁、还差多远；
   - `VOID BURST`：为什么炸（REACHED 谁 / TIME / GONE）、追了几 tick 几秒、离他倒下处多远、走了多远、炸到谁、各多少、以谁的名义（his / the form's / refused）、画面放没放、放逐了没有；
   - `VOID FALLBACK`：退路（为什么、彗星放没放）；`VOID WALK`：宿主不让挪单位、改由引擎走；`VOID DRAW`：显示钩子每 10 秒一行，引擎在形态走着 / 站着时各画了几次 run / idle、换了几次。
6. 测试开关：日志旁边放一个 `league_kogmaw.cfg`，写 `unit=off` 就不生成单位、照主包放彗星；`name=<名字>` 换一个单位名。

## 开发

```bash
python addons/league_kogmaw/make_override.py          # 主包的克格莫改了以后重新生成副本（--check 只比较，CI 用）
python tools/art/unit_kogmaw_void.py --review <目录>    # 形态的图（--check：仓库里的图是不是这个脚本画的）
python tools/art/fx_kogmaw_burst.py --review <目录>     # 爆炸的图
cd addons && cargo test -p league_kogmaw                 # 单元测试 + 迷你模拟（萨科附加包的 summon_mock.rs）
cargo build --release -p league_kogmaw                   # 单独的 league_kogmaw.dll（一般用合集 league_addons）
```
