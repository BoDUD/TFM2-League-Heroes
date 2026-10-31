<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 辛吉德 Singed

<img src="img/league_singed.png" alt="辛吉德" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_singed` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AP / Magic / Melee / Tank / CC |
| 高清帧 | PPU 1.39 |
| 附加包 | [辛吉德附加包](#附加包)（`league_singed`） |

![辛吉德演示](../preview/league_singed_showcase.gif)

其他预览：[逐帧预览](../preview/league_singed_frames.png)、[特效表](../preview/league_singed_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_singed.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.17 秒 · 攻击距离 20000*

用盾板砸。剧毒踪迹：一路在身后留下毒雾（3秒），雾里的敌人每0.5秒受13 + 13% 法强魔法伤害。剧毒冲流：经过敌方英雄身边时移速+25%（1.5秒）。

### 技能1 · 过肩摔

*冷却 1 秒 · 施放距离 20000 · 施放：指定目标 · 敌人（不含防御塔）*

抓住目标从肩膀上扔到身后，造成50 + 60% 法强魔法伤害和最大生命5%真实伤害；地上有强力粘胶时，被扔的敌人禁锢1秒。

### 技能2 · 强力粘胶

*冷却 1 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

扔出一瓶粘胶，地上留下3秒的一摊胶，里面的敌人减速50%并无法位移。

### 大招 · 疯狂药剂

*冷却 90 秒 · 施放距离 40000 · 施放：指定目标 · 敌方英雄*

喝下药剂，25秒内法强+60、双抗+30、移速+15%、每秒回复12生命；剧毒踪迹更大、伤害150%并附带重伤（治疗-40%）。

### 数值

攻击力 66（每级 +5）、法强 30（每级 +15）、生命 1260（每级 +115）、护甲 38（每级 +9）、魔抗 30（每级 +5）、移速 1050（每级 +11）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 辛吉德附加包

[辛吉德附加包](../../addons/league_singed/README.md)：`league_singed` v0.1.1

|  | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 过肩摔怎么飞 | 没有击飞：`Pull` 把目标从他身上拉过去，落到身后（数据里击飞和拉扯同时上，目标会被定在原地） | **击飞** `e_fly` tick（16），从他头顶飞过、落到他身后 `e_behind`（30000）远；路上碰到墙就落在墙边 |
| 落进粘胶禁锢 | 数据读不到单位站在哪：**只要地上有他的强力粘胶**，被摔的就禁锢 `e_root` tick | **真的落进胶里才禁锢** `e_root` tick（60） |

## 相关脚本和素材

- [`tools/kit/build_singed.py`](../../tools/kit/build_singed.py)
- [`tools/kit/setup_singed.py`](../../tools/kit/setup_singed.py)
- [`tools/lol/extract_singed.py`](../../tools/lol/extract_singed.py)
- [`tools/art/preview_singed.py`](../../tools/art/preview_singed.py)
- [`tools/art/rig_singed.py`](../../tools/art/rig_singed.py)
- [`assets/source/singed/`](../../assets/source/singed)

## 开发记录

> 下面是原来 README 里「英雄：辛吉德」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上路（Melee，标签 AP / Magic / Melee / Tank / CC），第 161 位英雄（I 组第一位）。炼金术士 辛吉德：又高又瘦、驼着背的光头老头，一只眼睛发白，灰绿蒙脸布、灰蓝围巾，红夹克和金扣带、带刺的护肩，背上一个发光的亮绿大药罐，近侧手臂上挂着一块高高的带刺盾板，另一只手拿着绿药瓶，深蓝细腿踩着一双大红棕靴子。技能方案 A（用户选）：过肩摔 / 强力粘胶 / 疯狂药剂，剧毒踪迹（Q）和剧毒冲流并进被动 |
| 普攻 / 被动 | 盾板砸（射程 20000，100% 攻击，防御塔也打）。**剧毒踪迹**：普攻和大招挂上的控制器（每 3 tick 一拍）在他脚下留毒雾——他站在哪团毒雾里就不再留新的（每团毒雾周围 9000 有一个只对他自己的感应圈），所以走路时身后留下一串、站着不动只有一团；毒雾半径 11000、存在 3 秒，里面的敌人每 0.5 秒受 13 + 13% 法强 魔法伤害（2026-10-25 起：毒雾的锚点原来 83 秒后才落地，倍速时几百个锚点同时在场很卡，修好后毒雾立刻出现，伤害从 20 + 20% 降到 13 + 13% 保持强度；用户「炼金的特效特别的卡 如果开倍速的话」；毒雾放在一个 1 单位的锚的结束效果里：区域直接放进动作不会生成）。**剧毒冲流**：敌方英雄在 22000 内（从他身边经过）时移速 +25% 1.5 秒，每 4 秒一次 |
| 技能1 | **过肩摔**（冷却 9 秒，射程 20000，对 `EnemyWithoutTower`：兵线野怪也摔）：抓住目标（第 10 tick），50 + 60% 法强 魔法伤害和目标最大生命 5% 的真实伤害（英雄联盟是按目标最大生命的魔法伤害，`ApAttack` 没有这个字段），把它从他身上拉过去 0.27 秒、落到他身后（`Pull` 直接作用在目标身上：放进投射物里的拉扯朝投射物自己去，原地不动；同时上击飞也会把人定住，所以主包不击飞）。地上有他的强力粘胶时被摔的敌人落地禁锢 1 秒（数据读不到单位站在哪，英雄联盟要真的落进胶里——附加包做） |
| 技能2 | **强力粘胶**（冷却 15 秒，射程 60000，对敌方英雄）：第 12 tick 扔出药瓶，0.33 秒后落在目标脚下，地上留 3 秒的一摊胶（半径 20000），里面的敌人减速 50%、不能放位移技能（`BlockMoveSkill`，英雄联盟的缚地） |
| 大招 | **疯狂药剂**（冷却 90 秒，对 40000 内的敌方英雄）：喝下药剂，25 秒内法强 +60、护甲和魔抗 +30、移速 +15%、每秒回复 12 生命；这段时间的毒雾半径 14000、伤害 150%，并让敌人受到的治疗 −40%（英雄联盟的重伤） |
| 连招 | 「有连招要做连招」，用户四个都要：**W → E**：粘胶落地后整段胶在地上的时间里（3 秒），过肩摔一好、射程里有敌方英雄就马上摔（被摔的人落地被粘住）；**E → 加速**：每次过肩摔都给他剧毒冲流的加速；**R → W**：喝完药（第 20 tick）粘胶马上又好，立刻扔向射程里的敌方英雄；**R 期间**：毒雾变大、伤害 150%、附带重伤，过肩摔冷却 9 → 6 秒。E、W 的冷却记在他身上的标记里（扎克 Q 的做法），连招才能放它们；技能位在冷却里点一下什么都不做。对局记录（种子 3）：W → E 第一版只在粘胶落地那一下看一次，14 次里 1 次（W 从 60000 扔、E 只够 20000），改成整段胶在地上都看之后 14 次里 7 次；R → W 3 / 3 |
| 数值 | 攻击 66（+5）、法强 30（+15）、生命 1200（+115）、护甲 38（+9）、魔抗 30（+5）、移速 1050（+11）、射程 20000 |
| 平衡 | 经典引擎模拟（上路，对斗士、处刑者、骑士、狂战士、枪骑兵、长柄战士，两边三套阵容；同一批对局俄洛伊 +1.39 / +1.08）：草稿 −0.12（过肩摔的拉扯和击飞一起上，人被定在原地没摔出去）；修好拉扯 +0.76；毒雾 18 + 18% 法强、生命 1200 +1.09；W → E 在整段胶在地上的时间里都能接 +1.53 / +1.56（种子 1-8 / 9-16）；控制器只认辛吉德自己（塞拉斯偷到大招不再带上毒雾和连招）后 +0.65 / +0.71；毒雾 20 + 20% 法强、生命 1260 定稿 +1.94（种子 1-8），和上路一档（K'Sante +1.34 / +2.19）。数据量：毒雾、加速和连招放在普攻挂上的控制器里（每 3 tick 一拍），技能 56、技能2 49 个节点 |
| 附加包 | `league_singed`（过肩摔，在 `league_addons` 合集里，[`addons/league_singed/README.md`](../../addons/league_singed/README.md)）：用户：「这个做附加包啊」——主包过肩摔的两处近似按英雄联盟做：**真的击飞**，目标击飞 0.27 秒从他头顶飞过、落到他身后 30000（路上碰到墙就落在墙边，墙格同波比附加包），每 tick 由附加包把它往落点挪一段；**落进胶里才禁锢**：落地后看三次它身上有没有粘胶的减速，有才禁锢 1 秒（飞的途中每 tick 摘掉这个减速，起飞前站的胶、空中经过的胶都不算）。佛耶戈 / 妮蔻的灵魂表、塞拉斯的职业表和可偷大招（偷到的疯狂药剂只给药剂的属性：毒雾、加速和连招的控制器只认辛吉德自己——普攻挂上的标记，不然塞拉斯偷完一分钟里也留毒雾、扔粘胶、过肩摔）、凯隐的攻击距离、大招按键的距离表都加上了辛吉德 |
| 精灵图（高清帧 PPU 1.39） | Codex 第 0 步画了 A（四分之三侧面）和 SA（[`tools/art/pack_singed_picture.py`](../../tools/art/pack_singed_picture.py)），[`tools/art/design_singed_hd.py`](../../tools/art/design_singed_hd.py) 按原图自己的格子读回（约 7.4–8 像素一格），[`tools/art/review_singed_size.py`](../../tools/art/review_singed_size.py) 摆在诺手、蒙多、厄加特、弗拉基米尔、普朗克、俄洛伊旁边给用户定大小；用户选了头顶到脚底 36 游戏像素、PPU 1.5、只做四分之三侧面。第 1 步两稿（[`tools/art/pack_singed_model.py`](../../tools/art/pack_singed_model.py)，16 像素一格），Codex 画成了约 18–19 像素一格，[`tools/art/design_singed_model.py`](../../tools/art/design_singed_model.py) 读回 A-1 42 × 58、A-2 45 × 62，都到不了 66 行；用户选了 A-2 原样：45 × 62，PPU 1.39（36 游戏像素）。动作：[`tools/art/pack_singed_poses.py`](../../tools/art/pack_singed_poses.py) 照英雄联盟的片段画了 11 个骨架姿势给 Codex（盾板当作近侧手里的一块硬板，背上的药罐跟着脖子走；英雄联盟的跑步是背影，不用）；Codex 的头和定稿一样大，身体却画大了 5%–35%（不那么 Q 版），[`tools/art/design_singed_poses.py`](../../tools/art/design_singed_poses.py) 按头的大小读回、换成定稿的颜色、贴回定稿的头，再按靴子的大小整行整列地删格子（头不动）把身体缩回定稿的大小（用户：「有问题的地方你直接修复」）。[`tools/art/rig_singed.py`](../../tools/art/rig_singed.py) 排成动作：待机、跑步（布隆的走法，用定稿自己的腿）、普攻（抡盾、砸下）、过肩摔（抓人、举过肩、甩出）、强力粘胶（扬手、扔出）、疯狂药剂（举药剂、发狂）、挨打（闪白）、阵亡（踉跄、坐倒）；姿势按两只脚的中点站，站着的脚不滑；审查只发一张合成 GIF，左边英雄联盟的同名动作，用户：「动作帧可以」 |
| 特效 | 14 张特效（[`tools/art/pack_singed_fx.py`](../../tools/art/pack_singed_fx.py) 的提示词，参考是英雄联盟里辛吉德自己的贴图，[`tools/lol/fx_ref_singed.py`](../../tools/lol/fx_ref_singed.py)），Codex 画回来，[`tools/art/import_singed_fx.py`](../../tools/art/import_singed_fx.py) 切成 `league_singed_fx` / `league_singed_big`（每张都核对了对称；毒雾和粘胶只画几帧，按区域存在的 3 秒拉开循环，禁锢的最后一帧停 1 秒）：盾板砸中，毒雾和喝药后的强化毒雾，过肩摔的抓住、落地的尘土、被粘住，飞出去的药瓶、地上的一摊胶、脚下的胶，喝药的爆发和身后的蒸汽，重伤标记，剧毒冲流的加速和脚下的气流 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_singed.py`](../../tools/lol/extract_singed.py)）：盾板挥动和砸中，过肩摔的出手、抓住、落地，毒雾的嘶嘶声（很轻：每团毒雾每拍对每个敌人都响），粘胶的扔出和落地，喝药，过肩摔的台词；粘胶和疯狂药剂在英雄联盟里没有台词，用他普攻的一句和大笑 |
| 图标 | 官方技能图标（过肩摔、强力粘胶、疯狂药剂，另有剧毒踪迹、剧毒冲流），从本地客户端取 |
| 选人卡片 | 药罐顶到脚底 45 游戏像素，卡片画布只装得下约 40：`league.dll` 的 UI_SIZES 画成 0.80、`banpick_center` −10（`tools/art/bp_card_audit.py`：待机的头顶在画布顶下约 2 像素，脚踩在下沿）。待机按 `tools/art/hero_reels.py` 剪：举起药瓶、举起药剂（这两帧手举得高，卡片上会切掉一点，卡片放的是另一条 bp 动画，不受影响）；选人卡片轮流放过肩摔、强力粘胶、疯狂药剂、普攻 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_singed.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_singed.py                     # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_singed.py                     # 五种语言的文字、音效配置、共享文件里他的键（脸 3,-31，卡片 -10）
python tools/art/design_singed_hd.py                 # Codex 第 0 步的原图读回（A、SA）
python tools/art/design_singed_model.py              # Codex 第 1 步的造型读回（A-2 原样，62 行）
python tools/art/design_singed_poses.py              # Codex 的姿势读回（贴回定稿的头，身体缩回定稿大小）
python tools/art/import_singed_fx.py                 # 特效 -> league_singed_fx / league_singed_big
python tools/art/rig_singed.py                       # 1 倍帧和 1.39 的原帧
python tools/art/ppu_restyle.py --hero singed        # 外描边、脸的位置
python tools/art/ppu_hd.py --hero singed             # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero singed         # 待机和选人卡片的小动作
python tools/art/preview_singed.py                   # 预览和演示 GIF
python addons/league_singed/make_override.py         # 附加包的辛吉德副本（主包的辛吉德改了以后要重跑）
```
