<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 卑尔维斯 Bel'Veth

<img src="img/league_belveth.png" alt="卑尔维斯" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_belveth` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / CC |
| 高清帧 | PPU 1.75 |
| 附加包 | [卑尔维斯附加包](#附加包)（`league_belveth`） |

![卑尔维斯演示](../preview/league_belveth_showcase.gif)

其他预览：[逐帧预览](../preview/league_belveth_frames.png)、[特效表](../preview/league_belveth_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_belveth.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 0.83 秒 · 攻击距离 24000*

用翼刃劈砍，出手很快。溶烛化紫：每放一个技能攻速+50%（4秒）；参与击杀敌方英雄后永久攻速+6%（最多8层）。

### 技能1 · 虚空激流

*冷却 1 秒 · 施放距离 40000 · 施放：指定目标 · 敌人（不含防御塔）*

朝目标突进并穿过去，对途经的所有敌人造成65 + 125% 攻击力物理伤害。

### 技能2 · 上觐沉渊

*冷却 1 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

甩尾砸地，冲击沿直线向前，造成75 + 115% 攻击力物理伤害，击飞0.83秒并减速40%（1.5秒）。

### 大招 · 万载豪筵

*冷却 80 秒 · 施放距离 35000 · 施放：指定目标 · 敌方英雄*

吞下珊瑚爆开：周围敌人受130 + 80% 攻击力物理伤害并减速40%；化为真身15秒：生命+20%、攻击距离增加、攻速+40%、移速+15%。真身被围攻时化为搠面皇锋：原地1.5秒减伤50%、吸血30%。

### 数值

攻击力 80（每级 +14）、生命 1100（每级 +100）、护甲 34（每级 +8）、魔抗 25（每级 +4）、移速 1000（每级 +11）、生命回复 2（每级 +1）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 卑尔维斯附加包

[卑尔维斯附加包](../../addons/league_belveth/README.md)：`league_belveth` v0.1.0

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 搠面皇锋（真身里的风暴） | 真身期间、`e_cd` 过了、`e_near` 内有两个敌方英雄就放 | 同样的风暴，但改成她**生命低于 `e_low`%**（默认 35%）时放，英雄联盟「残血时转风暴」 |
| 溶烛化紫（击杀叠的永久攻速） | 每层是一个永久 buff（`league_belveth_l1`…`l8`），死亡时引擎清掉全部 buff，每条命从零叠起 | 活着时记下每一层，死亡清掉后原样补回（最多 `l_max` 层） |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】用翼刃劈砍，出手很快。溶烛化紫：每放一个技能攻速+50%（4秒）；参与击杀敌方英雄后永久攻速+6%（最多8层，死亡后保留）。
- **大招 · 万载豪筵**：【附加包】吞下珊瑚爆开：周围敌人受130 + 80% 攻击力物理伤害并减速40%；化为真身15秒：生命+20%、攻击距离增加、攻速+40%、移速+15%。真身生命低于35%时化为搠面皇锋：原地1.5秒减伤50%、吸血30%。

## 相关脚本和素材

- [`tools/kit/build_belveth.py`](../../tools/kit/build_belveth.py)
- [`tools/kit/setup_belveth.py`](../../tools/kit/setup_belveth.py)
- [`tools/lol/extract_belveth.py`](../../tools/lol/extract_belveth.py)
- [`tools/art/preview_belveth.py`](../../tools/art/preview_belveth.py)
- [`tools/art/rig_belveth.py`](../../tools/art/rig_belveth.py)
- [`assets/source/belveth/`](../../assets/source/belveth)

## 开发记录

> 下面是原来 README 里「英雄：卑尔维斯」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 打野（Melee，标签 AD / Melee / CC），第 162 位英雄（I 组第二位）。虚空女皇 卑尔维斯：小小的深紫色脸、两只发光的品红眼睛、头顶品红的冠和金色饰片，两肩各竖一根高高的深紫长刺，胸口灰青象牙色的尖刺花饰，两只巨大的膜翼收拢时像斗篷一样裹住身体，下面粉紫色的爪子着地，身后拖一条长尾巴；贴地滑行，不迈步 |
| 普攻 / 被动 | 翼刃劈砍（射程 24000，每 50 tick 一下，80 攻击 +14/级，防御塔也打）。**溶烛化紫**：每放一个技能（Q、W、R、风暴）攻速 +50%，持续 4 秒；参与击杀敌方英雄（她打过的英雄 3 秒内死去，谁杀的都算：维戈的击杀窗口，被打的英雄身上挂一个每 tick 续一次的标记，她身上的控制器看着它断掉）永久攻速 +6%，最多 8 层（主包里层是 buff，死亡清掉；附加包补回）。英雄联盟里击杀大型野怪也叠层，没做：分不出一营野怪里哪只是大的 |
| 技能1 | **虚空激流**（冷却 4 秒，真身里 2 秒，射程 40000，对 `EnemyWithoutTower`：兵线野怪也冲）：第 3 tick 朝目标冲过去并穿过（`RushTime` 6000 × 7 tick，真身里 × 10 tick 冲得更远），途经的每个敌人受 65 + 125% 攻击 物理伤害 |
| 技能2 | **上觐沉渊**（冷却 10 秒，射程 45000，对 `EnemyWithoutTower`）：第 12 tick 甩尾砸地，一道冲击沿直线往前（长 55000、宽 7000，穿透），途经的敌人受 75 + 115% 攻击 物理伤害、击飞 50 tick、减速 40%（1.5 秒） |
| 大招 | **万载豪筵**（冷却 80 秒，对 35000 内的敌方英雄）：第 20 tick 吞下珊瑚爆开，周围 22000 的敌人受 130 + 80% 攻击 物理伤害、减速 40%（1.5 秒）；化为真身 15 秒：最大生命 +20%、攻击距离 +6000、攻速 +40%、移速 +15%。**搠面皇锋**并进真身：真身里被两个敌方英雄贴身（30000 内）时原地化为风暴 1.5 秒（冷却 12 秒）：受到伤害 −50%、吸血 30%，每 10 tick 斩一下她队伍最近打过的敌方英雄（20 + 50% 攻击）；附加包改成按真实生命（低于 35%） |
| 连招 | 「有连招要做连招」，用户四个都要：**W → Q**：甩尾击飞了敌方英雄，Q 的冷却马上清掉，控制器立刻朝那个英雄再冲一次；**Q → W**：冲过敌方英雄，W 好了就马上甩尾（要她这条命里自己放过一次 W，免得 3 级前就用出 W）；**吃珊瑚**：她参与击杀敌方英雄时，真身里就把真身续满 15 秒，不在真身里就把大招冷却砍到 40%；**真身 → Q**：真身里 Q 冷却减半、冲得更远，攻速也更高 |
| 数值 | 攻击 80（+14）、生命 1100（+100）、护甲 34（+8）、魔抗 25（+4）、移速 1000（+11）、射程 24000 |
| 平衡 | 经典引擎模拟（打野，对忍者、恶魔、猎人、狼人、吸血鬼，两边三套阵容；同一批对局雷克塞 +2.41）：草稿 +0.68（伤害不够；追踪一局：Q、W、R、风暴、击杀吃珊瑚、两个连招都在打）；Q 4 秒 60 + 120%、W 70 + 110%、攻击 76、生命 1060 +0.93；攻击 80 +14、生命 1100、护甲 34、技能后攻速 50% +1.52；再把 Q 缩到 3.5 秒、W 9 秒、伤害再加 +3.69（太强）；定稿 Q 65 + 125%、W 75 + 115%、R 130：+2.63 / +2.39（种子 1–8 / 9–16） |
| 附加包 | `league_belveth`（在 `league_addons` 合集里，[`addons/league_belveth/README.md`](../../addons/league_belveth/README.md)）：主包的两处近似按英雄联盟做：**风暴按真实生命**，真身里生命低于 35% 才化为风暴（主包是两个敌方英雄贴身）；**溶烛化紫的层死后不掉**，活着时记下每一层，死亡清掉后原样补回。普攻和大招的说明换成附加包自己的文字，游戏里看说明就知道副本生效了 |
| 精灵图（高清帧 PPU 1.75） | Codex 第 0 步画了 A（收翼）和 B（张翼）（[`tools/art/pack_belveth_picture.py`](../../tools/art/pack_belveth_picture.py)），[`tools/art/design_belveth_hd.py`](../../tools/art/design_belveth_hd.py) 按原图自己的格子读回（约 9.5–9.8 像素一格），[`tools/art/review_belveth_size.py`](../../tools/art/review_belveth_size.py) 摆在卡兹克、雷克塞、希瓦娜、狼人、扎克、奈德丽旁边，用户定了 A 收翼、头顶到爪尖 40、PPU 1.75。第 1 步（[`tools/art/pack_belveth_model.py`](../../tools/art/pack_belveth_model.py)）Codex 画了两稿，都比要的 14 像素格细，[`tools/art/design_belveth_model.py`](../../tools/art/design_belveth_model.py) 读回，用户挑了 A-1 裁到 82 行（86 × 82，两只眼睛都清楚）。动作：11 个骨架姿势（[`tools/art/pack_belveth_poses.py`](../../tools/art/pack_belveth_poses.py)：膜翼的前缘和翼膜、尾巴、爪子，头和肩刺不动），[`tools/art/design_belveth_poses.py`](../../tools/art/design_belveth_poses.py) 按头的大小读回、贴回定稿的头，身体按两肩圆珠的间距和头到爪尖的行数缩回定稿大小；[`tools/art/rig_belveth.py`](../../tools/art/rig_belveth.py) 按头对齐摆进动作：待机、滑行（整体上下浮动、爪子和尾巴错开摆）、普攻（举翼 → 劈下）、Q（放平往前冲）、W（扬尾 → 砸地）、风暴（双翼竖起 ↔ 横扫，两帧头在同一行，游戏里循环播放）、R（蜷缩 → 展开）、受击、死亡 |
| 特效 | 14 张特效（[`tools/art/pack_belveth_fx.py`](../../tools/art/pack_belveth_fx.py) 的提示词，参考是英雄联盟里卑尔维斯自己的贴图，[`tools/lol/fx_ref_belveth.py`](../../tools/lol/fx_ref_belveth.py)），Codex 画回来，[`tools/art/import_belveth_fx.py`](../../tools/art/import_belveth_fx.py) 切成 `league_belveth_fx` / `league_belveth_big`（每张都核对了对称；地裂是弹道，上下对称）：翼刃劈中、技能后的紫色气流、Q 起步和穿过的刀光、W 砸地和沿直线往前冲的地裂、击飞、减速、珊瑚爆发和命中、真身的紫光、吃珊瑚、风暴和斩中 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_belveth.py`](../../tools/lol/extract_belveth.py)）：翼刃挥动和劈中，Q 的出手和命中，W 的出手、砸地和命中，大招的出手、珊瑚爆发和命中，风暴和每一下斩击（很轻：每 10 tick 一下），吃珊瑚；W、风暴的台词；Q 和大招在英雄联盟里没有台词，用她普攻的一句和嘲讽 |
| 图标 | 官方技能图标（虚空激流、上觐沉渊、万载豪筵，另有搠面皇锋、溶烛化紫），从本地客户端取 |
| 选人卡片 | 肩刺到爪尖 47 游戏像素：`league.dll` 的 UI_SIZES 画成 0.82、`banpick_center` −8（`tools/art/bp_card_audit.py`：肩刺在画布顶下 1 像素，爪子踩在下沿）。待机按 `tools/art/hero_reels.py` 剪：蜷缩、滑行的上下浮动（举翼和扬尾那两帧比定稿高，放进待机卡片会切掉头）；卡片放普攻、甩尾、大招 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_belveth.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_belveth.py                    # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_belveth.py                    # 五种语言的文字、音效配置、共享文件里她的键（脸 0,-34，卡片 -8）
python tools/art/design_belveth_hd.py                # Codex 第 0 步的原图读回（A、B）
python tools/art/design_belveth_model.py             # Codex 第 1 步的造型读回（A-1 裁到 82 行）
python tools/art/design_belveth_poses.py             # Codex 的姿势读回（贴回定稿的头，身体缩回定稿大小）
python tools/art/import_belveth_fx.py                # 特效 -> league_belveth_fx / league_belveth_big
python tools/art/rig_belveth.py                      # 1 倍帧和 1.75 的原帧
python tools/art/ppu_restyle.py --hero belveth       # 外描边、脸的位置
python tools/art/ppu_hd.py --hero belveth            # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero belveth        # 待机和选人卡片的小动作
python tools/art/preview_belveth.py                  # 预览和演示 GIF
python addons/league_belveth/make_override.py        # 附加包的卑尔维斯副本（主包的卑尔维斯改了以后要重跑）
```
