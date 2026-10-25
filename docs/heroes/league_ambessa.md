<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 安蓓萨 Ambessa

<img src="img/league_ambessa.png" alt="安蓓萨" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_ambessa` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Shield / CC |
| 高清帧 | PPU 2（画成 85%） |
| 附加包 | [安蓓萨附加包](#附加包)（`league_ambessa`） |

![安蓓萨演示](../preview/league_ambessa_showcase.gif)

其他预览：[skills](../preview/league_ambessa_skills.gif)、[逐帧预览](../preview/league_ambessa_frames.png)、[特效表](../preview/league_ambessa_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_ambessa.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.17 秒 · 攻击距离 25000*

双刀。龙犬诡步：每放一个技能就朝目标冲一步，3秒内攻速+50%，下一刀加18 + 18% 攻击力+最大生命1%。铁令：敌方英雄靠近时举刀格挡，护盾80+80% 攻击力，然后砸地48 + 55% 攻击力，英雄再加最大生命3%。

### 技能1 · 暗袭

*冷却 1 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

身前横扫半圈，造成42 + 65% 攻击力+最大生命3%物理伤害；扫中后可接裂斩：直线劈下48 + 75% 攻击力，目标再加最大生命4%。

### 技能2 · 血戮

*冷却 1 秒 · 施放距离 25000 · 施放：指定目标 · 敌人（不含防御塔）*

甩链刀绕身一圈，造成38 + 52% 攻击力物理伤害并减速50%，持续1秒；冲刺后再甩一圈。

### 大招 · 公开处刑

*冷却 90 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

闪到敌方英雄身边压制0.6秒，再砸进地里：115 + 85% 攻击力+最大生命5%，眩晕0.6秒；此后护甲穿透+15%。

### 数值

攻击力 94（每级 +16）、生命 1000（每级 +92）、护甲 32（每级 +8）、魔抗 24（每级 +4）、移速 1050（每级 +12）、生命回复 2（每级 +1）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 安蓓萨附加包

[安蓓萨附加包](../../addons/league_ambessa/README.md)：`league_ambessa` v0.1.0

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 暗袭（Q） | 扫中的**都**额外吃最大生命 `q_pct`% | 只有**刀尖**（离她 `q_tip`% 半径以外）扫到的才加伤 |
| 裂斩（Q 第二段） | 加伤给**技能的目标** | 加伤给**直线上的第一个敌人**（离她最近的） |
| 铁令（W） | 砸地**总**对英雄加伤最大生命 `w_pct`% | 只有格挡时**被敌方英雄或野怪打到**，砸地才加伤，而且打中的所有敌人都加 |
| 公开处刑（R） | 闪到**技能的目标**身边 | 闪到她和目标这条线上（`r_range` 长、`r_w` 半宽）**最远的敌方英雄**身边 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】双刀。龙犬诡步：每放一个技能就朝目标冲一步，下一刀更快更重。铁令：敌方英雄靠近时举刀格挡得到护盾，然后砸地48 + 55% 攻击力；格挡时挨了英雄或野怪的打，砸地再加最大生命3%。
- **技能1 · 暗袭**：【附加包】暗袭向前扫半圈42 + 65% 攻击力，刀尖扫到的再加最大生命3%；扫中后可接裂斩：直线劈下48 + 75% 攻击力，第一个敌人再加最大生命4%。
- **大招 · 公开处刑**：【附加包】闪到她和目标这条线上最远的敌方英雄身边，压制0.6秒后砸进地里：115 + 85% 攻击力 + 最大生命5%，眩晕0.6秒。

## 相关脚本和素材

- [`tools/kit/build_ambessa.py`](../../tools/kit/build_ambessa.py)
- [`tools/kit/setup_ambessa.py`](../../tools/kit/setup_ambessa.py)
- [`tools/lol/extract_ambessa.py`](../../tools/lol/extract_ambessa.py)
- [`tools/art/preview_ambessa.py`](../../tools/art/preview_ambessa.py)
- [`tools/art/rig_ambessa.py`](../../tools/art/rig_ambessa.py)
- [`assets/source/ambessa/`](../../assets/source/ambessa)

## 开发记录

> 下面是原来 README 里「英雄：安蓓萨」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上单（Melee，标签 AD / Melee / Shield / CC），第 168 位英雄（J 组第三位）。铁血狼母 安蓓萨：诺克萨斯的战争女族长（梅尔的母亲），银白色往后梳的波浪短发、深棕色皮肤、红唇金耳环，肩上一圈深青绿色的尖毛领，黑铁胸甲、红围巾、红腰布，两只手各握一把带钩的月牙形龙犬刃，刀柄连着粗铁链 |
| 普攻 / 被动 | 双刀左右开弓（射程 25000，每 70 tick 一下）。**龙犬诡步**：每放一个技能，打中后 8 tick 朝目标冲一步（最远 45000），3 秒内攻速 +50%，下一刀额外 18 + 18% 攻击 + 最大生命 1% 物理伤害。**铁令**（控制器放）：敌方英雄进到 30000 内时举刀格挡，得到 80 + 80% 攻击 的护盾（1.5 秒），0.4 秒后砸地，25000 内的敌人受到 48 + 55% 攻击，英雄再加最大生命 3%（冷却 12 秒） |
| 技能1 | **暗袭**（冷却 8 秒，射程 30000）：身前半圈横扫，42 + 65% 攻击 + 最大生命 3% 物理伤害；扫中后 3 秒内可接**裂斩**（控制器对 40000 内最近的单位放）：从她到目标一条 40000 长的线劈下，48 + 75% 攻击，目标再加最大生命 4% |
| 技能2 | **血戮**（冷却 9 秒，射程 25000）：抡着铁链甩刀绕身一圈，24000 内 38 + 52% 攻击 物理伤害并减速 50% 1 秒；龙犬诡步冲到头再甩一圈 |
| 大招 | **公开处刑**（冷却 90 秒，射程 60000，对敌方英雄）：闪到它身边压制 0.6 秒，再砸进地里：115 + 85% 攻击 + 最大生命 5%，眩晕 0.6 秒；放过以后护甲穿透 +15%（阵亡后要再放一次） |
| 连招 | 「有连招要做连招」：**暗袭 → 裂斩**（英雄联盟的二段）：扫中后控制器马上砸地；**每个技能 → 龙犬诡步 → 强化普攻**；**血戮 → 冲刺 → 再甩一圈**；**公开处刑 → 暗袭 → 裂斩**：砸下后暗袭冷却清零马上横扫、再接裂斩，铁令也刷新（大招自己不再冲刺，横扫带着冲） |
| 数值 | 攻击 94（+16）、生命 1000（+92）、护甲 32（+8）、魔抗 24（+4）、移速 1050（+12）、射程 25000 |
| 平衡 | 经典引擎模拟（上路，对斗士、处刑人、骑士、狂战士、枪骑兵、长柄战士，两边三套阵容；同一批对局纳尔 +0.30、克烈 +0.13、约里克 +0.44）：草稿（攻击 96、暗袭 45 + 70% + 3%、裂斩 50 + 80% + 5%、血戮 40 + 55%、强化一刀 20 + 20% + 2%、铁令 50 + 60% + 4%、大招 120 + 90% + 6%）+1.74，太强；全面削到攻击 92 一档 −0.19；定稿（取中间，上面的数值）+0.59 / +0.42（种子 1–16 / 17–32） |
| 附加包 | `league_ambessa`（在 `league_addons` 合集里，[`addons/league_ambessa/README.md`](../../addons/league_ambessa/README.md)）：用户「和原版不一样的地方要做附加包」——**暗袭只有刀尖扫到的加伤**（主包里扫中的都加）；**裂斩的加伤给直线上第一个敌人**（主包给技能目标）；**铁令只有格挡时挨了英雄或野怪的打才加强**，而且打中的都加（主包总对英雄加）；**公开处刑闪到她和目标这条线上最远的敌方英雄**（主包闪到技能目标） |
| 精灵图（高清帧 PPU 2.0） | 云端会话：Codex 第 0 步画了 A（待机 3/4 正面）和 SA（侧面），第 1 步 Q 版模型选 A-1 / SA-1，头单独缩到身高的 27%（[`tools/art/design_ambessa_hd.py`](../../tools/art/design_ambessa_hd.py)，`hd/idle` 117×96，头发到脚底 48 游戏像素）。本地：姿势包照英雄联盟原版的帧（[`tools/art/pack_ambessa_poses.py`](../../tools/art/pack_ambessa_poses.py)，角色从她的动画按用途找，暗袭、裂斩、铁令、血戮、公开处刑、跑步各用自己的动画），Codex 画了 21 个姿势；[`tools/art/design_ambessa_poses.py`](../../tools/art/design_ambessa_poses.py) 按每张身体自己的比例读回（Codex 画的头比身子小 5–25%，按头读身子会忽大忽小），贴回定稿的头；[`tools/art/rig_ambessa.py`](../../tools/art/rig_ambessa.py) 摆成 11 个动作（idle run attack skill slam skill2 w ult step hit dead），暗袭的半圈刀光和龙犬诡步的拖影画进她自己的帧。局内 85%（用户「太大了安倍萨 整体模型缩小一点可以吗」：48 → 41 游戏像素，和德莱厄斯、盖伦的 42 差不多，`league.dll` 的 SIZES，帧往下 4 格） |
| 特效 | 20 张（[`tools/art/pack_ambessa_fx.py`](../../tools/art/pack_ambessa_fx.py) 的提示词，参考是英雄联盟里安蓓萨自己的贴图，[`tools/lol/fx_ref_ambessa.py`](../../tools/lol/fx_ref_ambessa.py)）：用户「每人做了一半」——前 10 张用户用 Gemini 画（[`tools/art/read_ambessa_gemini.py`](../../tools/art/read_ambessa_gemini.py) 去底、按游戏格子读回、做对称），后 10 张 Codex 画；[`tools/art/import_ambessa_fx.py`](../../tools/art/import_ambessa_fx.py) 切成 `league_ambessa_fx` / `league_ambessa_big`：双刀砍中、强化一刀、强化期间脚下的气流、冲到的尘土、暗袭扫中和刀尖、裂斩的裂缝（一条只带画面的线，亮 12 tick）和砸中、血戮的旋风和割中、减速、铁令的护盾、砸地、打中和加强、公开处刑闪走的烟、压制标记和砸出的坑 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_ambessa.py`](../../tools/lol/extract_ambessa.py)，23 段）：普攻的出手和打中、强化一刀、龙犬诡步，暗袭的出手、横扫和打中，裂斩的出手和砸地，血戮的出手、旋风和打中，铁令的格挡、砸地和打中，大招的出手、压制和砸下；配音：暗袭、裂斩、血戮、铁令、公开处刑 |
| 图标 | 官方技能图标（暗袭、血戮、公开处刑，另有裂斩、铁令、龙犬诡步），从本地客户端取 |
| 选人卡片 | 头发到脚底 48 游戏像素：界面缩到 0.81（`league.dll` 的 UI_SIZES），脸 (2, −35)、`banpick_center` −4（按 `tools/art/bp_card_audit.py` 的规则）。待机按 `tools/art/hero_reels.py` 剪进铁令格挡和举刀各一帧 |
| 俄洛伊的灵魂 | `tools/art/illaoi_souls.py` 加上安蓓萨（168 个），`league_illaoi` 0.2.5 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_ambessa.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_ambessa.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_ambessa.py                # 五种语言的文字、音效配置、共享文件里她的键（脸 2,-35，卡片 -4）
python tools/art/design_ambessa_poses.py         # Codex 的姿势读回（每张按身体自己的比例，贴回定稿的头）
python tools/art/read_ambessa_gemini.py          # Gemini 的 10 张特效读回
python tools/art/import_ambessa_fx.py            # 特效 -> league_ambessa_fx / league_ambessa_big
python tools/art/rig_ambessa.py                  # 1 倍帧和 2.0 的原帧（暗袭刀光、龙犬诡步拖影画进帧里）
python tools/art/ppu_restyle.py --hero ambessa   # 外描边、往下 4 格、脸的位置
python tools/art/ppu_hd.py --hero ambessa        # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero ambessa    # 待机和选人卡片的小动作
python tools/art/preview_ambessa.py              # 预览、演示 GIF 和每个技能单独的 GIF
python tools/art/illaoi_souls.py                 # 俄洛伊的灵魂（加了英雄或改了待机都要重跑），再跑 addons/league_illaoi/make_override.py
python addons/league_ambessa/make_override.py    # 附加包的安蓓萨副本（主包的安蓓萨改了以后要重跑）
```
