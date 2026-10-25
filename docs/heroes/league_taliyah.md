<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 塔莉垭 Taliyah

<img src="img/league_taliyah.png" alt="塔莉垭" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_taliyah` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / CC |
| 高清帧 | PPU 1.75 |
| 附加包 | [塔莉垭附加包](#附加包)（`league_taliyah`） |

![塔莉垭演示](../preview/league_taliyah_showcase.gif)

其他预览：[skills](../preview/league_taliyah_skills.gif)、[逐帧预览](../preview/league_taliyah_frames.png)、[特效表](../preview/league_taliyah_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_taliyah.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

甩出一块石子。浮石冲：脱战时移速+10%；放出墙幔后踩石冲浪，移速+40%（5秒）。

### 技能1 · 石穿

*冷却 6 秒 · 施放距离 90000 · 施放：地点 · 敌人（不含防御塔）*

朝目标方向一颗接一颗扔出5颗石头（扔出第一颗后可以移动），第一颗46 + 24% 法强魔法伤害，之后每颗23 + 12% 法强；脚下留下掘石场（8秒），站在上面施放改为一颗大石头：110 + 60% 法强并减速40%。

### 技能2 · 岩突

*冷却 1 秒 · 施放距离 80000 · 施放：指定目标 · 敌方英雄*

在身前地上撒下石雷（减速20%，4秒），目标脚下裂开后隆起，造成50 + 30% 法强魔法伤害并把敌人掀向自己；飞过石雷时石雷爆炸，造成38 + 24% 法强魔法伤害并眩晕0.4秒。

### 大招 · 墙幔

*冷却 70 秒 · 施放距离 90000 · 施放：指定目标 · 敌方英雄*

敌人在附近或已在交战：在目标处竖起长石墙（5秒），墙上的敌人被拖到她这一侧；敌人较远：从脚下拉出一道横墙，踩着石头沿墙冲刺，靠近敌人时跳下。碰到墙的敌人减速42%。

### 数值

攻击力 68（每级 +6）、法强 40（每级 +20）、生命 920（每级 +95）、护甲 19（每级 +6）、魔抗 26（每级 +4）、移速 890（每级 +9）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 塔莉垭附加包

[塔莉垭附加包](../../addons/league_taliyah/README.md)：`league_taliyah` v0.1.0

| 墙 | 主包（纯数据） | 附加包 |
|---|---|---|
| 竖墙（敌人近、或她已在打架） | 目标处一片竖长方形区域：立起时站在上面的敌人被拖到她那一侧，之后碰到的敌人减速 `r_slow`%（卡在墙边） | 同一块地方是真的墙：英雄、小兵、野怪、召唤物（两边都算，她自己也算）都过不去；立起时压在上面的单位推到她那一侧 |
| 横墙（敌人远：骑墙） | 从她脚下朝目标铺 `r_n` 段横长方形区域，碰到的敌人减速 | 每一段都是真的墙；她骑墙时站在墙顶上不受挡，跳下来那一 tick 推到近的一侧 |

## 相关脚本和素材

- [`tools/kit/build_taliyah.py`](../../tools/kit/build_taliyah.py)
- [`tools/kit/setup_taliyah.py`](../../tools/kit/setup_taliyah.py)
- [`tools/lol/extract_taliyah.py`](../../tools/lol/extract_taliyah.py)
- [`tools/art/preview_taliyah.py`](../../tools/art/preview_taliyah.py)
- [`tools/art/rig_taliyah.py`](../../tools/art/rig_taliyah.py)
- [`assets/source/taliyah/`](../../assets/source/taliyah)

## 开发记录

> 下面是原来 README 里「英雄：塔莉垭」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中路（Magician，标签 AP / Magic / Range / CC），第 163 位英雄（I 组第三位）。岩雀 塔莉垭：恕瑞玛的小姑娘，晒成麦色的皮肤，头顶高高盘起一大团棕发、发间一枚小金饰，肩上一圈米白的石片披肩，长长的红外套镶金边、前襟两条长摆的末端各坠一块灰石头，深靛色的上衣和裤子，紫色袖子、米白袖口，棕色靴子；移动时踩着一块石头冲浪 |
| 普攻 / 被动 | 甩出一块石子（射程 55000，每 90 tick 一下，68 攻击 +6/级）。**浮石冲**：脱战时移速 +10%（她打中英雄后 4 秒内算交战；英雄联盟是贴着地形加速，数据读不到地图上的墙）；放出墙幔后踩着墙冲浪，移速 +40%（5 秒） |
| 技能1 | **石穿**（冷却 6 秒，射程 90000）：朝目标方向一颗接一颗扔出 5 颗石头（相隔 12 tick，约 1 秒），扔出第一颗后就可以边走边扔；第一颗 46 + 24% 法强 魔法伤害，同一个目标之后每颗减半（23 + 12%）；脚下留下掘石场（8 秒） |
| 技能2 | **岩突**，合并 E **撒石阵**（冷却 16 秒，射程 80000，对敌方英雄）：先在身前地上（朝目标 25000）撒下石雷（减速 20%，4 秒），目标脚下裂开金色的裂纹预警，30 tick 后隆起，造成 50 + 30% 法强 魔法伤害并把敌人掀向自己；飞过石雷时石雷爆炸，造成 38 + 24% 法强 魔法伤害并眩晕 0.4 秒 |
| 大招 | **墙幔**（冷却 70 秒，射程 90000，对敌方英雄）。敌人在 60000 内、或她已在交战：目标处竖起一道长石墙（宽 12000、高 120000，5 秒），站在上面的被拖到她这一侧，之后碰到墙的敌人减速 42%（卡在墙边）。敌人较远：从脚下朝目标拉出一道横墙（6 段，每段 26000，Codex 画的横墙），她踩着石头沿墙顶一步一步冲过去（`RushTime` 2500 × 2 tick，最多 8 步），每一步前看一眼：55000 内有敌方英雄就提前跳下来，否则冲完再跳。主包里墙是区域（减速），附加包里是真的地形 |
| 连招 | 「有连招要做连招」，用户四个都要：**岩突穿过石雷 = 眩晕**（隆起把人掀向她，飞过石雷就炸）；**掘石场上的石穿 = 大石头**：站在自己的掘石场上再放，改为滚出一颗大石头（110 + 60%，减速 40% 1.5 秒）；**墙幔 → 岩突**：竖墙立起 30 tick 后马上对同一个英雄放岩突（岩突冷却重来），把人推到墙上撞晕 0.6 秒；骑墙跳下来时也马上放岩突，把人掀过石雷；**冲浪加速**：脱战和放完墙幔都加移速。墙幔 → 岩突只给塔莉垭自己（普攻挂一个永久标记）：塞拉斯偷到的大招只有墙和骑墙 |
| 数值 | 攻击 68（+6）、法术强度 40（+20）、生命 920（+95）、护甲 19（+6）、魔抗 26（+4）、移速 890（+9）、射程 55000 |
| 平衡 | 经典引擎模拟（中路，对火法师、冰法师、雷法师、风法师、白法师，两边三套阵容；同一批对局阿萝拉 +0.93、辛德拉 +1.17 / +1.42、艾尼维亚 +1.29）：草稿 +4.58（石雷每次都晕 50 tick，墙 99% 减速：全靠控制赢）；眩晕 24、墙 50%、冲浪 10%、伤害全砍 +0.47；伤害加回、墙加宽到 12000（比它 16 像素的图还窄，被拖出的英雄还站在墙里）+1.68 / +1.65；墙减速 42%、撞墙 36 tick +1.02 / +1.25。技能照英雄联盟重做后（Q 五颗石头、石雷撒在身前、骑横墙）：骑墙一口气 `MoveToTarget` 冲进人堆 −0.71 .. −1.28，改成一步一步、跳下点 55000 +1.48 / +2.21；墙幔只在岩突冷却好时接岩突 +1.42（32 个种子），但追踪发现 AI 总是先放岩突再放墙幔，撞墙一次都没出现；定稿留下墙幔 → 岩突（冷却重来），每一下伤害都砍：+1.62 / +1.39 / +1.73 / +1.38（种子 1–32，平均 +1.53） |
| 附加包 | `league_taliyah`（在 `league_addons` 合集里，[`addons/league_taliyah/README.md`](../../addons/league_taliyah/README.md)）：**墙幔的墙是真的地形**：竖墙和骑的横墙每一段，英雄、小兵、野怪、召唤物（两边都算）都过不去，进墙就退回去、只留顺着墙走的那一半；立墙时压在上面的推到一侧；她骑墙时站在墙顶上不受挡。大招的说明换成附加包自己的文字，游戏里看说明就知道副本生效了 |
| 精灵图（高清帧 PPU 1.75） | Codex 第 0 步画了 A（站立）和 B（踩石冲浪）（[`tools/art/pack_taliyah_picture.py`](../../tools/art/pack_taliyah_picture.py)），[`tools/art/design_taliyah_hd.py`](../../tools/art/design_taliyah_hd.py) 按原图自己的格子读回（约 9.8 像素一格），[`tools/art/review_taliyah_size.py`](../../tools/art/review_taliyah_size.py) 摆在中路法师旁边，用户定了 A 站立当待机、发顶到鞋底 40、PPU 1.75。第 1 步（[`tools/art/pack_taliyah_model.py`](../../tools/art/pack_taliyah_model.py)）Codex 画了两稿，[`tools/art/design_taliyah_model.py`](../../tools/art/design_taliyah_model.py) 读回，用户挑了 A-2（33 × 70）。动作：骨架姿势（[`tools/art/pack_taliyah_poses.py`](../../tools/art/pack_taliyah_poses.py)：每根骨头用定稿自己的长度，只改方向；冲浪的姿势站在石头上），[`tools/art/design_taliyah_poses.py`](../../tools/art/design_taliyah_poses.py) 按身体的比例读回（Codex 把身体画得比头大）、贴回定稿整个头（举手那一帧手臂画在头发上面，脸不盖住）；[`tools/art/rig_taliyah.py`](../../tools/art/rig_taliyah.py) 摆进动作：待机、踩石冲浪（石头上下浮动、前襟两条长摆跟着摆）、普攻（扬手 → 甩出）、石穿（举手 → 扔）、岩突（蹲下 → 推）、撒石阵（举手 → 横扫）、墙幔（召唤）和骑墙（踩着石头站在墙顶上）、受击、倒地 |
| 特效 | 14 张特效（[`tools/art/pack_taliyah_fx.py`](../../tools/art/pack_taliyah_fx.py) 的提示词，参考是英雄联盟里塔莉垭自己的贴图，[`tools/lol/fx_ref_taliyah.py`](../../tools/lol/fx_ref_taliyah.py)），另有第二次交付的横墙，Codex 画回来，[`tools/art/import_taliyah_fx.py`](../../tools/art/import_taliyah_fx.py) 切成 `league_taliyah_fx` / `league_taliyah_big`（每张都核对了对称；会漂的帧对齐、零碎的点清掉）：石子和它打中、石穿的石头和打中、大石头和打中、掘石场、岩突的裂纹预警和隆起、石雷和石雷爆炸、竖墙、横墙、减速、冲浪的扬沙 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_taliyah.py`](../../tools/lol/extract_taliyah.py)，17 段）：普攻的出手和打中（普攻自己的打中声没有音频，用 Q 打中的一段），石穿的每颗石头、打中、大石头和它打中，岩突的出手、隆起和打中，石雷落地和爆炸，墙幔的出手（R 出手那段没有音频，用远处施放的一段）、立墙和撞墙；Q、W、R 的台词（中文配音） |
| 图标 | 官方技能图标（石穿、岩突、墙幔，另有撒石阵、浮石冲），从本地客户端取 |
| 选人卡片 | 发顶到鞋底 40 游戏像素：`league.dll` 的 UI_SIZES 画成 0.98、脸 (1, −28)、`banpick_center` −10。待机按 `tools/art/hero_reels.py` 剪进普攻扬手、墙幔召唤各一帧 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_taliyah.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_taliyah.py                    # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_taliyah.py                    # 五种语言的文字、音效配置、共享文件里她的键（脸 1,-28，卡片 -10）
python tools/art/design_taliyah_hd.py                # Codex 第 0 步的原图读回（A、B）
python tools/art/design_taliyah_model.py             # Codex 第 1 步的造型读回（A-2，70 行）
python tools/art/design_taliyah_poses.py             # Codex 的姿势读回（按身体比例，贴回定稿的头）
python tools/art/import_taliyah_fx.py                # 特效 -> league_taliyah_fx / league_taliyah_big
python tools/art/rig_taliyah.py                      # 1 倍帧和 1.75 的原帧
python tools/art/ppu_restyle.py --hero taliyah       # 外描边、脸的位置
python tools/art/ppu_hd.py --hero taliyah            # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero taliyah        # 待机和选人卡片的小动作
python tools/art/preview_taliyah.py                  # 预览和演示 GIF（--only skills：每个技能单独一段，带字幕）
python addons/league_taliyah/make_override.py        # 附加包的塔莉垭副本（主包的塔莉垭改了以后要重跑）
```
