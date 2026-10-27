<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 可酷伯 Kobuko

<img src="img/tft_kobuko.png" alt="可酷伯" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_kobuko` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / CC / Shield |
| 高清帧 | PPU 2 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_kobuko_skills.gif)、[逐帧预览](../preview/tft_kobuko_frames.png)、[特效表](../preview/tft_kobuko_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_kobuko.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.2 秒 · 攻击距离 25000*

猫爪掌，造成100% 攻击力物理伤害。第二阶段：每条命第一次生命低于50%时进入狂怒，直到阵亡：攻击速度+40%、生命偷取20%。

### 技能1 · 金爪真言

*冷却 9.5 秒 · 施放距离 25000 · 施放：指定目标 · 敌人（不含防御塔）*

获得70 + 50% 法强的护盾（4秒）；4秒内下一次普攻变为金爪重掌，造成40 + 105% 攻击力 + 2%最大生命物理伤害并晕眩1秒。

### 技能2 · 猛虎扑

*冷却 10.5 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

扑向目标，落地时周围的敌人受到40 + 70% 攻击力 + 2%最大生命物理伤害并被击飞0.4秒。

### 大招 · 游戏结束！

*冷却 50 秒 · 施放距离 50000 · 施放：指定目标 · 敌方英雄*

一跃冲天（期间不可选中、免疫控制），砸落在敌方英雄身上：目标受到70 + 100% 攻击力 + 6%最大生命物理伤害，周围的敌人（含目标）再受到70 + 60% 攻击力 + 3%最大生命物理伤害并被击飞0.8秒。

### 数值

攻击力 80（每级 +13）、法强 20（每级 +10）、生命 1110（每级 +110）、护甲 36（每级 +8）、魔抗 28（每级 +4）、移速 1000（每级 +10）。

## 相关脚本和素材

- [`tools/kit/build_kobuko.py`](../../tools/kit/build_kobuko.py)
- [`tools/kit/setup_kobuko.py`](../../tools/kit/setup_kobuko.py)
- [`tools/lol/extract_kobuko.py`](../../tools/lol/extract_kobuko.py)
- [`tools/art/preview_kobuko.py`](../../tools/art/preview_kobuko.py)
- [`tools/art/rig_kobuko.py`](../../tools/art/rig_kobuko.py)
- [`assets/source/kobuko/`](../../assets/source/kobuko)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_kobuko`）的第七个英雄，上单（Melee，标签 AD / Melee / Tank / CC / Shield）。约德尔功夫老猫、武馆的大宗师。客户端里有四个他：第 14 赛季的赛博老大（五费，「游戏结束！」和被动「第二阶段」）、第 15 赛季的大宗师（二费重量级斗士，「金爪真言」：护盾 + 下一击加伤晕眩）、第 16 赛季的「可酷伯与悠米」、第 18 赛季的福星版；用户选了 **第 15 赛季的造型**和方案 A「金爪宗师」：第 15 赛季的金爪真言 + 第 14 赛季的第二阶段和游戏结束！，技能2 猛虎扑是我们加的。模型在 Riot 客户端的 `TFTSet15.wad.client`（`TFT15_Kobuko_15.skn`，一个子网格；十二段动作只有路径哈希，按内容命名） |
| 普攻 / 被动 | 猫爪掌（近战，100% 攻击）。**第二阶段**：每条命第一次生命低于 50% 时怒吼，进入狂怒直到阵亡：攻速 +40%、吸血 20%（tft.dll 的被动每拍看生命：数据读不到生命） |
| 技能1 | **金爪真言**（冷却 9.5 秒，在普攻距离内放，小兵野怪也放）：双臂一张，得 70 + 50% 法强的护盾 4 秒；4 秒内下一次普攻变成金爪重掌（播自己的 `claw` 动作：发光的掌心拍出去），造成 40 + 105% 攻击 + 2% 最大生命的物理伤害并晕眩 1 秒。蓄好时头顶转着一个金色漩涡 |
| 技能2 | **猛虎扑**（冷却 10.5 秒，距离 45000）：扑到目标身上（MoveToTarget），落地时 28000 以内的敌人受到 40 + 70% 攻击 + 2% 最大生命的物理伤害并被击飞 0.4 秒 |
| 大招 | **游戏结束！**（冷却 50 秒，敌方英雄在 50000 以内时放）：下蹲、一跃冲天（0.25 秒后看不见，在空中不可选中、免疫控制），目标脚下出现收紧的落点圈；0.6 秒时砸在目标身上（Teleport）：目标受到 70 + 100% 攻击 + 6% 最大生命的物理伤害，36000 以内的敌人（含目标）再受到 70 + 60% 攻击 + 3% 最大生命并被击飞 0.8 秒 |
| 数值 | 攻击 80（+13）、法强 20（+10）、生命 1110（+110）、护甲 36（+8）、魔抗 28（+4）、移速 1000（+10），攻击间隔 1.2 秒（以奥恩、瑟提、沃利贝尔为参照） |
| 平衡 | 经典引擎模拟（上单，对斗士、处刑者、骑士、狂战士、枪兵、长柄武士，两边三套阵容，纯数据版：狂怒算成第一次放大招时开始）：草稿 +5.64（同一批 league_sett +2.07），晕眩和击飞把对线锁死，空中无敌让他几乎不死（每局 0.74 次）；技能冷却拉长、晕眩 1 秒、击飞缩短 +2.83；再降伤害和属性 +1.61；取中间**定稿** +2.01 / +1.84（种子 1–8 / 9–16，league_sett +2.07 / +2.58） |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/kobuko.rs`](../../addons/tft/src/kobuko.rs)，和洛里斯、麦迪、希尔科、拉露恩、诺拉一起编成 `tft.dll`）：被动 `tft_kobuko:rage`（一半血时挂上永久的狂怒 buff，新的一条命开始时去掉）。`build_kobuko.py` 每次核对代码的默认参数和读写的名字都在数据里 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 | 他的大招本来就是纯数据，塞拉斯直接偷（特效表复制进附加包；`sylas_steal_check.py` 模拟里起跳、落点圈、砸地和击飞的特效 46 次）。佛耶戈 / 妮蔻的表（近战类）和俄洛伊的幽灵图（179 个）都加上了他 |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（捋胡子，金铲铲的待机）和 B（扎马步合掌），A 的格子约 9.75 px、约 100 格高，B 约 6.7 px 且身体只有 A 的四分之三，[`tools/art/design_kobuko_hd.py`](../../tools/art/design_kobuko_hd.py) 按各自的格子读回；用户定 **A-1、高 40、PPU 2.0**（[`tools/art/design_kobuko_model.py`](../../tools/art/design_kobuko_model.py)：76×80）。姿势包的骨架是他自己的动作按帧投影出来的（[`tools/art/pack_kobuko_poses.py`](../../tools/art/pack_kobuko_poses.py)：模型本来就是 Q 版，头只放大 1.1 倍；举手过头那帧比画布还高，换成半举）。Codex 画了 16 个姿势，用自己的九十来种颜色、比定稿略小：[`tools/art/design_kobuko_poses.py`](../../tools/art/design_kobuko_poses.py) 把颜色换回定稿的、所有帧统一放大 1.05（按头自动找比例会在 1.00–1.12 之间跳，身体忽大忽小）、贴回定稿的头（倒地的两帧保留 Codex 自己倒着画的头）；[`tools/art/rig_kobuko.py`](../../tools/art/rig_kobuko.py) 按 Codex 在格子上画的位置摆放，拼成普攻（蓄力 → 推掌 → 收势）、金爪重掌（`claw`）、技能1（抬臂 → 张臂）、技能2 和大招（深蹲 → 腾空 → 双掌砸落）、受击、阵亡（后仰 → 前扑 → 趴下）。**跑步**：Codex 的四帧跑步近处的腿一直在前、远处的腿一直在后（会滑步，洛里斯的教训），改成布隆 / 泰坦的走法：定稿自己的两条短腿轮流抬起、往前迈，8 帧 |
| 特效 | 13 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_kobuko_fx.py`](../../tools/art/pack_kobuko_fx.py) 的提示词，参考是金铲铲里他自己第 15、14 赛季的粒子贴图 [`tools/lol/fx_ref_kobuko.py`](../../tools/lol/fx_ref_kobuko.py)），全部左右对称：金色护盾、蓄好的金色漩涡、金爪掌印、晕眩星星、扑击落地环、起跳尘土、落点圈、砸地冲击波、击飞尘土、第二阶段的火焰。[`tools/art/import_kobuko_fx.py`](../../tools/art/import_kobuko_fx.py) 切成 `tft_kobuko_fx` / `tft_kobuko_big`；金色漩涡原本贴在他抬起的额头上，挪到头顶上方；狂怒的火焰放在身后（盖在身上看不清人） |
| 音效 | 他自己的金铲铲音效（Riot 客户端 Map22：第 15 赛季 `MODE_TFT_Set15_Champs_SFX` 的掌击、命中、重击、金色护盾、晕眩、击飞和猛砸；第 14 赛季的第二阶段变身、跃起和重击），大招配第 14 赛季的英文语音（WeGame 没有金铲铲语音包）（[`tools/lol/extract_kobuko.py`](../../tools/lol/extract_kobuko.py)，12 段） |
| 选人卡片 | 发髻到脚底 40 游戏像素：`banpick_center` −6（bp_card_audit 的规则：lo_idle 在中心上方 32.7），不另设缩放。脸 (−1, −33)。待机按 `tools/art/hero_reels.py` 剪进收势和抬臂的帧，卡片轮播技能1、普攻、技能2、大招 |

重新生成（素材来自本机的金铲铲客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_kobuko.py --riot "D:\Riot Games\League of Legends" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_kobuko.py                  # 技能数据（调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_kobuko.py                  # 五种语言的文字、音效配置、tft 包共享文件里他的键
python tools/art/design_kobuko_hd.py              # Codex 第 0 步的原图读回
python tools/art/design_kobuko_model.py           # 定稿 A-1 缩到 80 行
python tools/art/design_kobuko_poses.py           # Codex 的姿势（定稿的颜色、统一大小和头）
python tools/art/import_kobuko_fx.py              # 特效 -> tft_kobuko_fx / tft_kobuko_big，图标
python tools/art/rig_kobuko.py                    # 1 倍帧和 2.0 的原帧（跑步是布隆的走法）
python tools/art/ppu_restyle.py --hero kobuko     # 外描边
python tools/art/ppu_hd.py --hero kobuko          # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_kobuko  # 待机和选人卡片的小动作
python tools/art/preview_kobuko.py                # 预览和每个技能单独的 GIF
python tools/art/review_kobuko_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py       # 塞拉斯偷到的游戏结束！
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试（可酷伯、洛里斯、麦迪、希尔科、拉露恩、诺拉）
```
