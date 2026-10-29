<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 瑟庄妮 Sejuani

<img src="img/league_sejuani.png" alt="瑟庄妮" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_sejuani` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AP / Melee / CC / Tank |
| 高清帧 | PPU 2 |
| 附加包 | [瑟庄妮附加包](#附加包)（`league_sejuani`） |

![瑟庄妮演示](../preview/league_sejuani_showcase.gif)

其他预览：[skills](../preview/league_sejuani_skills.gif)、[逐帧预览](../preview/league_sejuani_frames.png)、[特效表](../preview/league_sejuani_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_sejuani.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.17 秒 · 攻击距离 25000*

链枷抽打。北地之怒：脱战后冰霜护甲，护甲、魔抗+40%。普攻和凛冬之怒叠霜冻，满4层冻住1秒并造成60 + 40% 法强；打中被她晕住的敌人再造成其最大生命6%。

### 技能1 · 极寒突袭

*冷却 1 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

钢鬃冲向目标，路上的敌人受到80 + 70% 法强魔法伤害并被击飞0.5秒。

### 技能2 · 凛冬之怒

*冷却 1 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

链枷先横扫一圈造成40 + 40% 法强，再往前砸出一道冰造成60 + 60% 法强魔法伤害，都减速40%1.5秒。

### 大招 · 极冰寒狱

*冷却 70 秒 · 施放距离 70000 · 施放：指定目标 · 敌方英雄*

甩出冰套索，第一个敌方英雄受到170 + 80% 法强魔法伤害并被眩晕1.25秒；落点冰风暴减速周围敌人35%，持续2秒。

### 数值

攻击力 76（每级 +6）、法强 30（每级 +15）、生命 1300（每级 +120）、护甲 44（每级 +10）、魔抗 30（每级 +5）、移速 1000（每级 +11）、生命回复 2（每级 +1）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 瑟庄妮附加包

[瑟庄妮附加包](../../addons/league_sejuani/README.md)：`league_sejuani` v0.1.1

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 永冻领域（霜冻叠满冻住） | 霜冻层数记在瑟庄妮自己身上（`f1`…`f3`），打不同的敌人也叠在一起 | 层数挂在**每个敌方英雄自己身上**（`league_sejuani_frost`），某一个满 `f_n` 层才冻住它 |
| 碎冰 | 只认她自己的眩晕（冻住、Q 击飞、R）之后的下一击 | 她打中的英雄**正被眩晕或击飞**就碎冰，**队友控的也算**；每个英雄单独冷却 `sh_cd` |
| 冰霜护甲 | 护甲、魔抗 + 韧性（游戏没有免疫减速，用韧性代替）；只有她自己出手才算进入战斗 | 护甲在身时每 tick 清掉她身上所有减速（**免疫减速**，副本不给韧性）；**受到伤害**也算进入战斗 |
| 极寒突袭 | 冲到目标为止，路上的敌人都击飞 | **撞到第一个敌方英雄就停下**（冲锋剩下的时间按在原地） |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】链枷抽打。北地之怒：脱战后冰霜护甲，护甲、魔抗+40%、免疫减速。普攻和凛冬之怒给每个敌方英雄叠霜冻，满4层冻住1秒并造成60 + 40% 法强；打中被晕住的敌人（谁晕的都算）再造成其最大生命6%。
- **技能1 · 极寒突袭**：【附加包】钢鬃冲向目标，撞到第一个敌方英雄就停下，路上的敌人受到80 + 70% 法强魔法伤害并被击飞0.5秒。

## 相关脚本和素材

- [`tools/kit/build_sejuani.py`](../../tools/kit/build_sejuani.py)
- [`tools/kit/setup_sejuani.py`](../../tools/kit/setup_sejuani.py)
- [`tools/lol/extract_sejuani.py`](../../tools/lol/extract_sejuani.py)
- [`tools/art/preview_sejuani.py`](../../tools/art/preview_sejuani.py)
- [`tools/art/rig_sejuani.py`](../../tools/art/rig_sejuani.py)
- [`assets/source/sejuani/`](../../assets/source/sejuani)

## 开发记录

> 下面是原来 README 里「英雄：瑟庄妮」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 打野（Melee，标签 AP / Melee / CC / Tank），第 165 位英雄（I 组第五位；计划里是辅助替补，用户选了打野）。北地之怒 瑟庄妮：骑着战猪钢鬃的弗雷尔卓德女战士，青铜金头盔上一对蓝冰角，冰蓝眼睛，紫皮甲配青铜金尖肩甲和蓝宝石，米白毛领，棕黑相间的链枷末端一个蓝色冰锤；钢鬃灰蓝毛、白鬃毛、两根象牙色大獠牙。技能方案 A（用户选）：技能1 极寒突袭、技能2 凛冬之怒、大招 极冰寒狱，被动北地之怒里并入永冻领域（霜冻叠满冻住）和碎冰 |
| 普攻 / 被动 | 链枷抽打（射程 25000，每 70 tick 一下，76 攻击 +6/级）。**北地之怒**：5 秒没出手就有冰霜护甲（护甲、魔抗 +40%，韧性 30 代替免疫减速；进入战斗后再留 2 秒）。**永冻领域**：普攻和凛冬之怒每下叠一层霜冻（5 秒），满 4 层冻住打中的英雄 1 秒并造成 60 + 40% 法强 魔法伤害（主包的层数记在她自己身上：数据读不到别人的 buff；附加包记在每个敌人身上）。**碎冰**：她自己眩晕 / 冻住 / 击飞一个英雄后 1.5 秒内，下一击再造成 30 + 40% 法强 魔法伤害 + 目标最大生命 6% 的真实伤害（5 秒一次；附加包里队友的眩晕也算） |
| 技能1 | **极寒突袭**（冷却 7 秒，射程 45000）：钢鬃冲向目标（每 tick 6000、8 tick），路上的敌人受到 80 + 70% 法强 魔法伤害并被击飞 0.5 秒（附加包：撞到第一个敌方英雄就停下） |
| 技能2 | **凛冬之怒**（冷却 4.5 秒，射程 30000）：第 10 tick 链枷横扫一圈（半径 22000）40 + 40% 法强，第 26 tick 往前砸出一道冰（45000 长、7000 宽）60 + 60% 法强，都是魔法伤害、减速 40% 1.5 秒、每下叠一层霜冻 |
| 大招 | **极冰寒狱**（冷却 70 秒，射程 70000，对敌方英雄）：甩出冰套索（每 tick 12000，80000 远），第一个敌方英雄受到 170 + 80% 法强 魔法伤害并眩晕 1.25 秒；落点冰风暴（半径 26000）2 秒里减速周围敌人 35% |
| 连招 | 「有连招要做连招」，用户四个都要：**Q 撞飞 → 马上 W**：冲锋撞中英雄，凛冬之怒冷却清零并立刻挥出（她自己放过一次 W 之后）；**W 叠满霜冻 → 冻住**：两下挥击就是两层；**晕住 → 碎冰**（上面的被动）；**R 冻住 → Q 冲过去**：套索冻住英雄，极寒突袭冷却清零，眩晕期间对射程里的英雄冲过去。R → Q 只有瑟庄妮自己会（塞拉斯偷到的极冰寒狱只有套索） |
| 数值 | 攻击 76（+6）、法术强度 30（+15）、生命 1300（+120）、护甲 44（+10）、魔抗 30（+5）、移速 1000（+11）、射程 25000 |
| 平衡 | 经典引擎模拟（打野，对忍者、恶魔、猎人、狼人、吸血鬼，两边三套阵容；扎克同一批对局 +1.58 / +1.30）：草稿 −1.16（生命 1150、Q 60 + 60% 每 8 秒、W 30 + 30% / 50 + 50% 每 6 秒、R 120）；生命 1250、攻击 76、Q 80 + 70% 每 7 秒、W 40 + 40% / 60 + 60% 每 5 秒、R 150：+1.23 / +0.33；再加生命 1300、护甲 44：+1.27；W 每 4.5 秒、R 170、碎冰 30、冻住 60 = 现在的数值，16 组种子平均 +1.40（扎克 +1.44）。附加包的规则经典引擎跑不了，数值按主包定 |
| 附加包 | `league_sejuani`（在 `league_addons` 合集里，[`addons/league_sejuani/README.md`](../../addons/league_sejuani/README.md)）：用户「和英雄联盟不一样的地方都是做附加包」——**霜冻记在每个敌方英雄身上**，满 4 层冻住它；**碎冰对谁的眩晕都算**（每个英雄单独冷却）；**冰霜护甲免疫减速**（护甲在身时清掉身上的减速，副本不给韧性），**受到伤害也算进入战斗**；**极寒突袭撞到第一个敌方英雄就停下**。英雄联盟里队友近战普攻也叠霜冻，附加包接口看不到队友的普攻，没做 |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（骑着钢鬃待机）和 B（极寒突袭冲锋）（[`tools/art/pack_sejuani_picture.py`](../../tools/art/pack_sejuani_picture.py)），[`tools/art/design_sejuani_hd.py`](../../tools/art/design_sejuani_hd.py) 按原图自己的格子（约 5.6 px）读回；用户定冰角尖到蹄子 36 游戏像素、A 待机、B 冲锋给跑步和 Q。第 1 步（[`tools/art/pack_sejuani_model.py`](../../tools/art/pack_sejuani_model.py)）用户选了 A-2 / B-1，又要求「先调高ppu像素吧」：PPU 2.0，Codex 照选中的两稿在更细的格子上重画（[`tools/art/pack_sejuani_redraw.py`](../../tools/art/pack_sejuani_redraw.py)），[`tools/art/design_sejuani_model.py`](../../tools/art/design_sejuani_model.py) 读回到 72 / 76 行（用户又选了 A-2 / B-1）。动作：Codex 照骑手 + 野猪 + 链枷的骨架画了 14 个姿势（[`tools/art/pack_sejuani_poses.py`](../../tools/art/pack_sejuani_poses.py)，英雄联盟每个动作的同一帧作参考），[`tools/art/design_sejuani_poses.py`](../../tools/art/design_sejuani_poses.py) 读回：贴回定稿的头（人立那帧留 Codex 自己往后仰的头），钢鬃按定稿野猪脸的大小缩回（Codex 画大了 1.05–1.3 倍）；[`tools/art/rig_sejuani.py`](../../tools/art/rig_sejuani.py) 按獠牙尖对齐拼成待机、跑步、普攻、Q、W、R、受击、死亡 |
| 特效 | 15 张特效（[`tools/art/pack_sejuani_fx.py`](../../tools/art/pack_sejuani_fx.py) 的提示词，参考是英雄联盟里瑟庄妮自己的贴图，[`tools/lol/fx_ref_sejuani.py`](../../tools/lol/fx_ref_sejuani.py)），Codex 画回来，[`tools/art/import_sejuani_fx.py`](../../tools/art/import_sejuani_fx.py) 切成 `league_sejuani_fx` / `league_sejuani_big`：冰锤砸中、冲锋的雪雾和撞飞、凛冬之怒的横扫冰环和往前飞的冰线、冻住的冰笼、碎冰、冰霜护甲、霜冻雪花（附加包）、减速、冰套索、套中的冰晶、冰风暴。凛冬之怒第二下只用往前飞的冰线（她身上的单向画面在红色方不会镜像） |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_sejuani.py`](../../tools/lol/extract_sejuani.py)，17 段）：普攻的出手和打中，冲锋和撞中，凛冬之怒的出手、横扫、砸地和打中，冻住，碎冰，大招的出手、甩出、冻住和冰风暴；配音：Q、W、R 的施法语音 |
| 图标 | 官方技能图标（极寒突袭、凛冬之怒、极冰寒狱，另有永冻领域、北地之怒），从本地客户端取 |
| 选人卡片 | 冰角尖到蹄子 36 游戏像素、41 宽：不缩小（`league.dll` 的 UI_SIZES 只能缩小），脸 (3, −28)、`banpick_center` −12（冰角在卡片顶下面，蹄子在底边）。待机按 `tools/art/hero_reels.py` 剪进甩链枷、甩套索各一帧 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_sejuani.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_sejuani.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_sejuani.py                # 五种语言的文字、音效配置、共享文件里她的键（脸 3,-28，卡片 -12）
python tools/art/design_sejuani_hd.py            # Codex 第 0 步的原图读回（A、B）
python tools/art/design_sejuani_model.py         # Codex 的 PPU 2.0 重画读回（A-2 待机、B-1 冲锋）；--round 1 是第一轮
python tools/art/design_sejuani_poses.py         # Codex 的姿势读回（贴回定稿的头，钢鬃缩回定稿大小）
python tools/art/import_sejuani_fx.py            # 特效 -> league_sejuani_fx / league_sejuani_big
python tools/art/rig_sejuani.py                  # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero sejuani   # 外描边、脸的位置
python tools/art/ppu_hd.py --hero sejuani        # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero sejuani    # 待机和选人卡片的小动作
python tools/art/preview_sejuani.py              # 预览、演示 GIF 和每个技能单独的 GIF
python addons/league_sejuani/make_override.py    # 附加包的瑟庄妮副本（主包的瑟庄妮改了以后要重跑）
```
