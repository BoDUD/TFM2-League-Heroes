<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 克烈 Kled

<img src="img/league_kled.png" alt="克烈" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_kled` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Shield |
| 高清帧 | PPU 2 |
| 附加包 | [克烈附加包](#附加包)（`league_kled`） |

![克烈演示](../preview/league_kled_showcase.gif)

其他预览：[skills](../preview/league_kled_skills.gif)、[逐帧预览](../preview/league_kled_frames.png)、[特效表](../preview/league_kled_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_kled.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.07 秒 · 攻击距离 25000*

挥斧。斯嘎尔替他挡伤害（500 + 140% 攻击力），没了就下马：攻击-10%，不能比武、冲锋；打人攒勇气，满了上马。暴烈秉性：每10秒四下快攻，第四下多50 + 30% 攻击力+最大生命6%。

### 技能1 · 飞索捕熊器

*冷却 1 秒 · 施放距离 55000 · 施放：指定目标 · 敌人（不含防御塔）*

扔捕熊夹造成60 + 60% 攻击力；夹住英雄减速40%，1.5秒后再造成90 + 140% 攻击力并拽过来。下马时是随身手枪：40 + 100% 攻击力，自己往后跳。

### 技能2 · 比武

*冷却 1 秒 · 施放距离 40000 · 施放：指定目标 · 敌人（不含防御塔）*

斯嘎尔冲过目标造成60 + 80% 攻击力物理伤害，加速50%；穿过英雄还会再冲回来一次。

### 大招 · 冲啊——！！

*冷却 90 秒 · 施放距离 90000 · 施放：指定目标 · 敌方英雄*

带护盾（150 + 150% 攻击力）冲向敌方英雄，撞上造成110 + 60% 攻击力+最大生命8%并击退；身边队友加速40%。

### 数值

攻击力 100（每级 +17）、生命 1040（每级 +90）、护甲 32（每级 +8）、魔抗 22（每级 +4）、移速 1050（每级 +12）、生命回复 2（每级 +1）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 克烈附加包

[克烈附加包](../../addons/league_kled/README.md)：`league_kled` v0.1.0

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 斯嘎尔的血 | 一层护盾当斯嘎尔的血，旁边的 `league_kled_sk` 跟着护盾走（WithShield）：大招的护盾也会让斯嘎尔"活着" | 本包**自己记斯嘎尔的血**：这条命第一次骑上 `sk_hp` + 攻击 `sk_ad`%，勇气满了重新骑上 `re_hp` + 攻击 `re_ad`%，骑着时受到的伤害从这里扣，扣完就让他下马 |
| 捕熊夹的绳子 | 夹住的英雄跑多远都会被拽回来 | 被夹住的英雄离克烈超过 `q_break`，**绳子断**，不拽 |
| 下马的样子 | 只有出招（普攻、手枪）是步行的克烈，站着、跑着、挨打还是骑着斯嘎尔 | **整身步行**：下马时站着、跑着、挨打和普攻第一帧都画步行的克烈 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】挥斧。斯嘎尔有自己的血（500 + 140% 攻击力），替他挡伤害，打空就下马：攻击-10%，不能比武、冲锋；打人攒勇气，满了上马。暴烈秉性：每10秒四下快攻，第四下多50 + 30% 攻击力+最大生命6%。
- **技能1 · 飞索捕熊器**：【附加包】扔捕熊夹造成60 + 60% 攻击力；夹住英雄减速40%，1.5秒后再造成90 + 140% 攻击力并拽过来，它跑太远绳子会断。下马时是随身手枪：40 + 100% 攻击力，自己往后跳。

## 相关脚本和素材

- [`tools/kit/build_kled.py`](../../tools/kit/build_kled.py)
- [`tools/kit/setup_kled.py`](../../tools/kit/setup_kled.py)
- [`tools/lol/extract_kled.py`](../../tools/lol/extract_kled.py)
- [`tools/art/preview_kled.py`](../../tools/art/preview_kled.py)
- [`tools/art/rig_kled.py`](../../tools/art/rig_kled.py)
- [`assets/source/kled/`](../../assets/source/kled)

## 开发记录

> 下面是原来 README 里「英雄：克烈」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上单（Melee，标签 AD / Melee / Shield），第 166 位英雄（J 组第一位）。暴怒骑士 克烈：骑着大蜥蜴斯嘎尔的约德尔老兵，一对大尖耳朵，青绿红边帽子上一根钢尖刺，米白大胡子，一只瞎眼，咧嘴狂笑露尖牙，拿小双刃斧和绳子拴的捕熊夹；斯嘎尔橙黄鳞片、紫肚子、青蓝头刺、一只黄绿大眼睛、两条细长紫腿。斯嘎尔被打跑后克烈下马步行，双手拿大双刃斧，还会掏一把短火枪 |
| 普攻 / 被动 | 挥斧（射程 25000，每 64 tick 一下，100 攻击 +17/级）。**怯战蜥蜴斯嘎尔**：每条命骑着斯嘎尔出场，斯嘎尔的血是一层 500 + 140% 攻击 的护盾，替他挡伤害；打空了斯嘎尔逃跑，克烈下马：攻击 −10%，比武和大招放不了（大招冷却按 10 秒算）；下马时打人攒勇气（打中英雄两格、别的一格，另外每 2 秒一格），10 格满了斯嘎尔回来，带 180 + 60% 攻击 的血、加速 40% 2 秒。**暴烈秉性**（W 并进普攻）：每 10 秒一次，接下来 4 秒攻速 +150%，四下快攻，第四下多 50 + 30% 攻击 + 目标最大生命 6% |
| 技能1 | **飞索捕熊器**（冷却 8 秒，射程 55000）：扔出捕熊夹，打中第一个敌人 60 + 60% 攻击；夹住英雄时减速 40% 1.5 秒，然后再造成 90 + 140% 攻击 并把它拽过来（20000）。下马时是**随身手枪**：往前喷一枪（45000 长、9000 宽，穿透）40 + 100% 攻击，自己往后跳 12000，打中英雄攒两格勇气 |
| 技能2 | **比武**（冷却 9 秒，射程 40000，只在骑着时）：斯嘎尔冲过目标 60 + 80% 攻击，加速 50% 1 秒；穿过英雄 0.7 秒后、2.5 秒内会对 60000 里的英雄再冲回来一次（英雄联盟的第二段） |
| 大招 | **冲啊——！！**（冷却 90 秒，射程 90000，对敌方英雄，只在骑着时）：先给自己 150 + 150% 攻击 的护盾 4 秒、身边队友加速 40%，斯嘎尔冲到英雄面前，撞上造成 110 + 60% 攻击 + 目标最大生命 8% 并击退，撞的地方的队友也加速 |
| 连招 | 「有连招要做连招」：**Q 拽过来 → 马上 E**：拽人那一下之后比武就绪就立刻冲过去；**E 穿过英雄 → 再冲一次 → 暴烈秉性就绪**：第二段穿过后 W 冷却清零；**R 撞中 → 马上 Q**：撞到英雄后捕熊夹冷却清零并立刻扔出；**重新上马 → 暴烈秉性就绪** |
| 数值 | 攻击 100（+17）、生命 1040（+90）、护甲 32（+8）、魔抗 22（+4）、移速 1050（+12）、射程 25000；斯嘎尔 500 + 140% 攻击 |
| 平衡 | 经典引擎模拟（上路，对斗士、处刑人、骑士、狂战士、枪骑兵、长柄战士，两边三套阵容；纳尔同一批对局 +0.01 / +0.59）：草稿 −3.36（生命 760、攻击 88、斯嘎尔 360 + 120%、下马 −20%）；生命 920、攻击 94、下马 −10%、斯嘎尔 420、技能加伤 −1.44；生命 1000、攻击 98、护甲 32、斯嘎尔 480 + 140%、Q 60 / 90 + 140% 每 8 秒、E 60 + 80% 每 9 秒、W 50 + 6%、R 110：−0.22 / +0.08；再加生命 1040、攻击 100、斯嘎尔 500 = 现在的数值 +0.48 / +0.09（平均 +0.29，纳尔 +0.30） |
| 附加包 | `league_kled`（在 `league_addons` 合集里，[`addons/league_kled/README.md`](../../addons/league_kled/README.md)）：用户「和英雄联盟不一样的地方都是做附加包」——**斯嘎尔自己的血**（主包的护盾标记会被大招护盾"续命"）；**捕熊夹的绳子会断**（被夹住的英雄跑出 60000 就不拽）；**下马整身步行**（站着、跑着、挨打也是步行的克烈） |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（骑着斯嘎尔待机）和 B（下马的克烈）（[`tools/art/pack_kled_picture.py`](../../tools/art/pack_kled_picture.py)，下马的模型是同一个 WAD 里的 KledRider，按同一个世界比例渲染），[`tools/art/design_kled_hd.py`](../../tools/art/design_kled_hd.py) 按原图自己的格子（约 5 px）读回；用户定帽尖到爪子 40 游戏像素、PPU 2.0。第 1 步（[`tools/art/pack_kled_model.py`](../../tools/art/pack_kled_model.py)）每格 14 px，用户挑 A-1（80 行）和 B-1；B-1 只画了 52 行、头小一圈，换上 A-1 的头（[`tools/art/design_kled_model.py`](../../tools/art/design_kled_model.py) `head_swap`），两种形态同一张脸。动作是 Codex 照骨架画的 20 个姿势（[`tools/art/pack_kled_poses.py`](../../tools/art/pack_kled_poses.py)：骑乘 11 个、步行 9 个），[`tools/art/design_kled_poses.py`](../../tools/art/design_kled_poses.py) 读回、贴回定稿的头、把画大了的斯嘎尔和步行身子缩回定稿大小，[`tools/art/rig_kled.py`](../../tools/art/rig_kled.py) 拼成 13 个标签：骑乘的 idle run attack skill skill2 ult hit dead 和步行的 f_idle f_run f_attack f_skill f_hit（死亡都是步行的克烈倒下，英雄联盟骑着死也是 Rider_Death） |
| 特效 | 21 张特效（[`tools/art/pack_kled_fx.py`](../../tools/art/pack_kled_fx.py) 的提示词，参考是英雄联盟里克烈自己的贴图，[`tools/lol/fx_ref_kled.py`](../../tools/lol/fx_ref_kled.py)），Codex 画回来，[`tools/art/import_kled_fx.py`](../../tools/art/import_kled_fx.py) 切成 `league_kled_fx` / `league_kled_big`：斧头砍中、暴烈秉性的怒火和第四下重击、飞出去的捕熊夹和夹住、脚上的夹子、拽回来、手枪的霰弹和火药烟、比武的尘土和斩光、加速风线、冲锋的护盾、撞地冲击波、斯嘎尔逃跑的烟尘和回来的怒火 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_kled.py`](../../tools/lol/extract_kled.py)，25 段）：普攻的出手和打中，暴烈秉性的开始、第四下和打中，捕熊夹的扔出、夹住和拽，手枪的开火和打中，比武两段和打中，大招的出手、撞上和打中，斯嘎尔逃跑和回来；配音：Q、W、E、R、手枪、下马、上马 |
| 图标 | 官方技能图标（飞索捕熊器、比武、冲啊——！！，另有暴烈秉性、怯战蜥蜴斯嘎尔、随身手枪），从本地客户端取 |
| 选人卡片 | 帽尖到爪子 41 游戏像素：界面缩到 0.95（`league.dll` 的 UI_SIZES），脸 (2, −28)、`banpick_center` −12（帽尖在卡片顶下面，爪子在底边）。待机按 `tools/art/hero_reels.py` 剪进扔夹子、拽绳子各一帧（举斧那一帧会把帽子顶出卡片），步行待机剪进掏枪 |
| 俄洛伊的灵魂 | `tools/art/illaoi_souls.py` 加上克烈（166 个），`league_illaoi` 0.2.2 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_kled.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_kled.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_kled.py                # 五种语言的文字、音效配置、共享文件里他的键（脸 2,-28，卡片 -12）
python tools/art/design_kled_hd.py            # Codex 第 0 步的原图读回（A、B）
python tools/art/design_kled_model.py         # Codex 第 1 步读回（A-1 骑乘、B-1 换上 A-1 的头）
python tools/art/design_kled_poses.py         # Codex 的姿势读回（贴回定稿的头，斯嘎尔和步行身子缩回定稿大小）
python tools/art/import_kled_fx.py            # 特效 -> league_kled_fx / league_kled_big
python tools/art/rig_kled.py                  # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero kled   # 外描边、脸的位置
python tools/art/ppu_hd.py --hero kled        # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero kled    # 待机和选人卡片的小动作
python tools/art/preview_kled.py              # 预览、演示 GIF 和每个技能单独的 GIF
python tools/art/illaoi_souls.py              # 俄洛伊的灵魂（加了英雄或改了待机都要重跑），再跑 addons/league_illaoi/make_override.py
python addons/league_kled/make_override.py    # 附加包的克烈副本（主包的克烈改了以后要重跑）
```
