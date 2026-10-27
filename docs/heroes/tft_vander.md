<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 范德尔 Vander

<img src="img/tft_vander.png" alt="范德尔" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_vander` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / CC |
| 高清帧 | PPU 2 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_vander_skills.gif)、[逐帧预览](../preview/tft_vander_frames.png)、[特效表](../preview/tft_vander_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_vander.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.07 秒 · 攻击距离 25000*

挥拳造成100% 攻击力物理伤害。监察：受到的伤害降低10%，生命高于50%时降低20%。

### 技能1 · 地下猎犬

*冷却 10 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

摆出防御姿态，嘲讽周围的敌人0.75秒，获得40护甲和30魔抗（2.5秒）；下一拳造成40 + 140% 攻击力物理伤害，队里每有一个家人再加40% 攻击力。

### 技能2 · 铁拳突进

*冷却 10 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

冲向敌人打出上勾拳，造成50 + 90% 攻击力物理伤害并晕眩0.5秒，身边的敌人受到35%的伤害。

### 大招 · 桥头死守

*冷却 50 秒 · 施放距离 50000 · 施放：指定目标 · 敌方英雄*

跳进敌群砸地，周围的敌人受到150 + 150% 攻击力物理伤害并被击飞1秒；之后4秒内受到的伤害降低15%，身边每个敌方英雄再降低8%（最多4个）。

### 数值

攻击力 78（每级 +14）、生命 1080（每级 +105）、护甲 34（每级 +8）、魔抗 26（每级 +4）、移速 1030（每级 +11）。

## 相关脚本和素材

- [`tools/kit/build_vander.py`](../../tools/kit/build_vander.py)
- [`tools/kit/setup_vander.py`](../../tools/kit/setup_vander.py)
- [`tools/lol/extract_vander.py`](../../tools/lol/extract_vander.py)
- [`tools/art/preview_vander.py`](../../tools/art/preview_vander.py)
- [`tools/art/rig_vander.py`](../../tools/art/rig_vander.py)
- [`assets/source/vander/`](../../assets/source/vander)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_vander`）的第八个英雄，打野（Melee，近战斗士）。祖安地下城的老拳手、蔚和爆爆的养父，戴着红铜色大铁拳套（《双城之战》）。金铲铲第 13 赛季的二费（`TFT13_Prime`，家人 / 监察者，射程 1，生命 800，法力 0/50），只有一个技能「地下猎犬」（停手摆出防御姿态 2.5 秒嘲讽周围、加双抗，下一击换成 400% 攻击的重击，每个一二费队友再 +100%；英雄强化版晕眩 0.75 秒并溅射 35%）和监察者羁绊（减伤，一半血以上更多）。用户选了**打野**和方案 A「监察·地下猎犬」：被动和技能1 照金铲铲，技能2 铁拳突进、大招桥头死守是我们加的。模型在 Riot 客户端的 `TFTSet13.wad.client`（`tft13_prime.skn`，一个子网格；动作只有路径哈希，按内容命名；拳套绑在右手骨骼上） |
| 普攻 / 被动 | 铁拳（近战，100% 攻击，打塔）。**监察**：一直少受 10% 伤害，生命高于一半时 20%（tft.dll 的被动每拍看生命：数据读不到生命） |
| 技能1 | **地下猎犬**（冷却 10 秒，距离 30000，小兵野怪也放）：沉身摆出防御姿态，26000 以内的敌人被嘲讽 0.75 秒，自己 2.5 秒内 +40 护甲、+30 魔抗；5 秒内下一拳换成重击：40 + 140% 攻击，场上每个家人队友（爆爆、蔚、金克丝）再 +40% 攻击（tft.dll） |
| 技能2 | **铁拳突进**（冷却 10 秒，距离 45000）：蓄着身子冲到目标身上（MoveToTarget），到达时一记上勾拳（播自己的 `upper` 动作）：50 + 90% 攻击并晕眩 0.5 秒，22000 以内的敌人（含目标）再受到这一拳的 35% |
| 大招 | **桥头死守**（冷却 50 秒，敌方英雄在 50000 以内时放）：跳向目标（MoveToTarget），落地举起拳套砸进地面（播自己的 `slam` 动作）：34000 以内的敌人受到 150 + 150% 攻击并被击飞 1 秒；之后 4 秒少受 15% 伤害，砸地时身边每个敌方英雄再 +8%（最多 4 个，tft.dll） |
| 数值 | 攻击 78（+14）、生命 1080（+105）、护甲 34（+8）、魔抗 26（+4）、移速 1030（+11），攻击间隔约 1.07 秒（以狼人、蔚、瑟提为参照；金铲铲的他是坦克，生命护甲高、攻击低） |
| 平衡 | 经典引擎模拟（打野，对忍者、恶魔、猎人、狼人、吸血鬼，两边三套阵容，纯数据版：监察按固定 15% 算）：草稿 +8.18（同一批 league_vi +2.08、league_warwick +0.57），每次放技能1 都嘲讽一圈，团战被他拖住；嘲讽缩到 0.75 秒、半径 26000，冷却拉长，重击和技能2 降伤害、晕眩 0.5 秒，属性往下调，**定稿** +2.15 / +1.07（种子 1–8 / 9–16，league_vi +2.08 / +1.99，league_warwick +0.57 / +0.52）。tft.dll 里按血量的监察、家人加成和大招按人数的减伤没有进模拟 |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/vander.rs`](../../addons/tft/src/vander.rs)，和可酷伯、洛里斯、麦迪、希尔科、拉露恩、诺拉一起编成 `tft.dll`）：被动 `tft_vander:watcher`（按血量改减伤），`tft_vander:family`（重击按家人队友加伤害），`tft_vander:stand`（大招落地按身边敌方英雄数加减伤）。`build_vander.py` 每次核对代码的默认参数和数据一致 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 | 他的大招用了 tft.dll，塞拉斯偷到的是纯数据版（`sylas_ult()`：砸地、击飞和固定 15% 减伤，特效表复制进附加包；`sylas_steal_check.py` 模拟里起跳、砸地、冲击波、击飞的特效都出来了）。佛耶戈 / 妮蔻的表（近战类）和俄洛伊的幽灵图都加上了他（共 181 个） |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（站立）和 B（格斗架势）两张，用户定 **B-2、高 40、PPU 2.0**（[`tools/art/design_vander_model.py`](../../tools/art/design_vander_model.py)：81×80，额头被取成米色的格子换回肤色）。姿势包的骨架是他自己的动作按帧投影出来的（[`tools/art/pack_vander_poses.py`](../../tools/art/pack_vander_poses.py)，头放大 1.6 倍对上定稿），Codex 画了 15 个姿势；[`tools/art/design_vander_poses.py`](../../tools/art/design_vander_poses.py) 把颜色换回定稿的、贴回定稿的头；[`tools/art/rig_vander.py`](../../tools/art/rig_vander.py) 按 Codex 在格子上画的位置摆放，拼成普攻（后仰 → 前冲砸拳 → 收势）、技能1（下沉 → 举拳套护头）、技能2（蓄身冲刺，到达才播上勾拳）、大招（蓄身 → 腾空，落地才播举拳 → 砸地）、受击、阵亡（踉跄 → 扑倒）。**跑步**（review：「跑步姿势不像啊」）：第一版是定稿蹲着的格斗架势配布隆 / 泰坦的走法，不像金铲铲里直起身子的小跑；按他自己的跑步动画做了 8 帧的跑步包（[`tools/art/pack_vander_run.py`](../../tools/art/pack_vander_run.py)，每帧写明两只靴子该落在哪一格），Codex 重画，读回时清掉它自己画的脸和头发（「头发不干净吧？」），缩到 0.75（「怎么体型现在这么大啊 跑步的时候」：站直跑约 125 行，缩后约 90 行、45 游戏像素，头保持定稿大小），8 帧 × 133 毫秒 |
| 特效 | 13 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_vander_fx.py`](../../tools/art/pack_vander_fx.py) 的提示词，参考是金铲铲里他自己的粒子贴图 [`tools/lol/fx_ref_vander.py`](../../tools/lol/fx_ref_vander.py)），全部左右对称：监察的钢蓝波纹、防御姿态、嘲讽标记、蓄好的拳光、重击、冲刺尘土、上勾拳、晕眩星星、腾空、砸地冲击波、击飞碎石、死守的余烬。[`tools/art/import_vander_fx.py`](../../tools/art/import_vander_fx.py) 切成 `tft_vander_fx` / `tft_vander_big`；Codex 缩成的 64 px 图标糊了，从它的高清原稿重新缩 |
| 音效 | 他自己的金铲铲音效（Riot 客户端 Map22 `MODE_TFT_Set13_Champs_SFX`：普攻、暴击、技能施放和强化、英雄强化版的命中），起跳和砸地借蔚的大招，大招配第 13 赛季的英文语音（WeGame 没有金铲铲语音包）（[`tools/lol/extract_vander.py`](../../tools/lol/extract_vander.py)，11 段） |
| 选人卡片 | 头发到脚底 40 游戏像素：`banpick_center` −6，不另设缩放。脸 (8, −34)（架势把头探在前面）。待机按 `tools/art/hero_reels.py` 剪进防御姿态和收势的帧，卡片轮播普攻、技能1、砸地、上勾拳 |

重新生成（素材来自本机的金铲铲客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_vander.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_vander.py                  # 技能数据（调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_vander.py                  # 五种语言的文字、音效配置、tft 包共享文件里他的键
python tools/art/design_vander_hd.py              # Codex 第 0 步的原图读回
python tools/art/design_vander_model.py           # 定稿 B-2 缩到 80 行
python tools/art/design_vander_poses.py           # Codex 的姿势和跑步（定稿的颜色和头）
python tools/art/import_vander_fx.py              # 特效 -> tft_vander_fx / tft_vander_big，图标
python tools/art/rig_vander.py                    # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero vander     # 外描边
python tools/art/ppu_hd.py --hero vander          # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_vander  # 待机和选人卡片的小动作
python tools/art/preview_vander.py                # 预览和每个技能单独的 GIF
python tools/art/review_vander_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py       # 塞拉斯偷到的桥头死守
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试（范德尔、可酷伯、洛里斯、麦迪、希尔科、拉露恩、诺拉）
```
