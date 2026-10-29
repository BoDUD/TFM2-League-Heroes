<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 诺姆希 Nomsy

<img src="img/tft_nomsy.png" alt="诺姆希" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_nomsy` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / Dot |
| 高清帧 | PPU 2.6 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_nomsy_skills.gif)、[逐帧预览](../preview/tft_nomsy_frames.png)、[特效表](../preview/tft_nomsy_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_nomsy.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

吐出小火团，造成100% 攻击力物理伤害。龙神之躯：生命值低于40%时每秒回复3%最大生命值。

### 技能1 · 火球！

*冷却 4 秒 · 施放距离 60000 · 施放：指定目标 · 敌人（不含防御塔）*

抛出大火球，爆炸造成90 + 63% 法强魔法伤害，再弹出2颗小火球打附近的敌人，各造成55%伤害。

### 技能2 · 龙息

*冷却 7 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

向前喷出扇形龙息，造成55 + 36% 法强魔法伤害并灼烧2秒，魔抗降低20%（4秒）。

### 大招 · 龙神飞升

*冷却 50 秒 · 施放距离 70000 · 施放：指定目标 · 敌方英雄*

飞上天空（减伤50%、免疫控制），降下10颗火球，各造成60 + 35% 法强魔法伤害；落地后攻速+30%、法强+25%（5秒）。

### 数值

攻击力 80（每级 +6）、法强 40（每级 +20）、生命 1020（每级 +104）、护甲 18（每级 +7）、魔抗 20（每级 +4）、移速 880（每级 +9）。

## 相关脚本和素材

- [`tools/kit/build_nomsy.py`](../../tools/kit/build_nomsy.py)
- [`tools/kit/setup_nomsy.py`](../../tools/kit/setup_nomsy.py)
- [`tools/lol/extract_nomsy.py`](../../tools/lol/extract_nomsy.py)
- [`tools/art/preview_nomsy.py`](../../tools/art/preview_nomsy.py)
- [`tools/art/rig_nomsy.py`](../../tools/art/rig_nomsy.py)
- [`assets/source/nomsy/`](../../assets/source/nomsy)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_nomsy`）的第十七个英雄，中路（Magician，远程法师）。金铲铲第 7 赛季（巨龙之巢）的三费 `TFT7_Nomsy`「诺姆希」（龙神 / 龙族小天才，法系输出，射程 4）：一只四肢着地蹲坐的胖小龙，粉色大圆肚子和粉色的脸、额头紫色花纹带、绿眼睛、地包天的嘴和白獠牙、头顶三根紫刺，深紫蓝的背鳞，紫红翼膜的小翅膀，短粗带刺的尾巴。技能「火球！」：朝随机敌人抛火球，落地爆炸再弹出几颗小火球。用户选的方案 A「龙神飞升」：技能1 沿用火球！，被动取龙神羁绊的每秒回血，技能2 龙息和大招龙神飞升是我们自己的 |
| 普攻 / 被动 | **小火团**（远程 55000，打塔）：第 9 tick 从嘴里吐出一颗追踪火团，100% 攻击力。**龙神之躯**：生命值高于法师的基准（1020 + 104），生命值低于 40% 时每秒回复 3% 最大生命值；数据读不到生命，由 tft.dll 每拍看她的生命，回血时身上亮 `p_heal` |
| 技能1 | **火球！**（冷却 4 秒，距离 60000，打野怪也会放）：起身吼一声，第 18 tick 跳起抛出大火球，24 tick 后落在目标脚下爆炸，22000 以内 90 + 63% 法强魔法伤害；tft.dll 在爆炸处生成 2 颗小火球，飞向 45000 以内最近的、爆炸没炸到的敌人（不够时才轮到炸到的），各 55% 伤害 |
| 技能2 | **龙息**（冷却 7 秒，距离 45000）：仰头吸气，第 12 tick 往前喷出扇形火焰（半径 62000，和火焰画面一样长），55 + 36% 法强魔法伤害，灼烧 2 秒（每 0.5 秒 10 + 6% 法强），魔抗 −20%（4 秒） |
| 大招 | **龙神飞升**（冷却 50 秒，距离 70000，有敌方英雄时）：展开翅膀飞起来盘旋约 2.7 秒，期间减伤 50%、免疫控制；第 24 tick 起每 12 tick 一颗、共 10 颗火球从天上砸向 70000 以内随机的敌人，各 60 + 35% 法强魔法伤害；落地后攻速 +30%、法强 +25%（5 秒） |
| 数值 | 攻击 80（+6）、法强 40（+20）、生命 1020（+104）、护甲 18（+7）、魔抗 20（+4）、移速 880（+9），攻击间隔 1.5 秒，射程 55000 |
| 平衡 | 经典引擎模拟（中路，对原版炎术师、冰法、雷法、风法、白法师，两边三套阵容，纯数据版：回血换成固定的每秒回复，小火球换成落点附近随机的敌人）：草稿 −2.73（同一批 tft_aoshin 纯数据版 +0.64，换一批种子 +1.23）；Q 每 4 秒 90 + 65%、E 70 + 45%、R 60 + 35% … 小火球 55%、爆炸半径 22000、R 10 颗 +0.59 / +1.82；龙息的扇形加到火焰画面的长度（62000）后 +1.66 / +1.75，龙息 55 + 36%、Q 63% **+1.12 / +1.16** = 定稿 |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/nomsy.rs`](../../addons/tft/src/nomsy.rs)，和其他 tft 英雄一起编成 `tft.dll`）：被动 `tft_nomsy:dragon`（低血每秒回血，死亡时播她的死亡音效）；效果 `bounce`（大火球落地时在落点生成小火球）和 `ember`（小火球命中）。日志写到 `%APPDATA%/TeamSamoyed/TeamfightManager2/data/tft_nomsy.log`（SPAWN / HEAL / BOUNCE / EMBER）。`build_nomsy.py` 每次核对代码的默认参数和数据一致 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 / 悠米 | 龙神飞升本身没有 tft.dll 的部分，塞拉斯照常偷到（特效表复制进附加包）。佛耶戈 / 妮蔻的表（法师）、俄洛伊的幽灵图和悠米骑上去的高度都加上了她 |
| 精灵图（高清帧 PPU 2.6） | 参考是金铲铲客户端里她自己的模型（一个子网格一张贴图；动作片段按路径找到 idle / run / attack / spell / death / celebration）。Codex 第 0 步画了 A（3/4 蹲坐）和 B（更侧面）；提示词把细长带月牙翼膜的近侧翅膀写成了尾巴，Codex 看了模型改正过来，骨骼上核对过（L_Wing 是翅膀，Tail 是后腿后面那条短粗尾巴）。原稿约 7.5 px 一格，按它自己的格子读回。用户定 **A-1、36 游戏像素、PPU 2.6**（[`tools/art/design_nomsy_model.py`](../../tools/art/design_nomsy_model.py)：129×94，一格一个像素，近处的瞳孔补成 2×2）。姿势包的骨架是她自己的动作按帧投影出来的（[`tools/art/pack_nomsy_poses.py`](../../tools/art/pack_nomsy_poses.py)：舌头收回嘴里；展翅的帧翅膀缩到一半；盘旋三帧身体用待机的朝向，翅膀按定稿的长度画方向线），Codex 画了 20 个姿势，这次严格按 7 px 一格；[`tools/art/design_nomsy_poses.py`](../../tools/art/design_nomsy_poses.py) 一格一格取回、换成定稿的颜色。走路 8 帧（0.6 秒一整个循环）按肚子中心对齐（Codex 的各帧前后差了 29 格）。大招：起飞、上扬 / 平展 / 下扇循环扇翅膀、落地 |
| 特效 | 13 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_nomsy_fx.py`](../../tools/art/pack_nomsy_fx.py) 的提示词，参考是她自己第 7 赛季的粒子贴图和斯莫德、小龙的火焰 [`tools/lol/fx_ref_nomsy.py`](../../tools/lol/fx_ref_nomsy.py)）。四张会飞的（小火团、大火球、小火球、龙息）朝右、上下对称，其余左右对称。[`tools/art/import_nomsy_fx.py`](../../tools/art/import_nomsy_fx.py) 按 Codex 的 1 倍版切成 `tft_nomsy_fx` 和 `tft_nomsy_big`；龙息放在从嘴边出发的一条只有画面的线上（100000 长，火焰左端在嘴边），灼烧上方像个小灰人的烟去掉了；飞升光环画在她身后（盖在身上像她自己着火），图标用 Codex 的 64×64 |
| 音效 | 普攻、大火球发射和命中、小火球发射和命中、两句语音是她自己的金铲铲音效（Riot 客户端 Map22 里还留着的第 7 赛季音效包，按路径哈希读）；起飞、落地、火球雨借峡谷的火龙，小火团命中、大招吼声、飞升、死亡借斯莫德，回血借希瓦娜（龙形 W），龙息借安妮（W），灼烧借布兰德（被动）（[`tools/lol/extract_nomsy.py`](../../tools/lol/extract_nomsy.py)，19 段） |
| 选人卡片 | 翅膀顶到脚底 36 游戏像素：`banpick_center` (2, −14)（按规则 −39 减去最高点 −25.3），不另设缩放。脸 (15, −25)（两眼之间）。待机按 `tools/art/hero_reels.py` 剪进普攻帧，卡片轮播普攻、火球！、龙息、龙神飞升 |

重新生成（素材来自本机的金铲铲客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_nomsy.py --riot "D:\Riot Games\League of Legends" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_nomsy.py                  # 技能数据（被动和小火球调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_nomsy.py                  # 五种语言的文字、音效配置、tft 包共享文件里她的键
python tools/art/design_nomsy_hd.py              # Codex 第 0 步的原图读回
python tools/art/design_nomsy_model.py           # 定稿 A-1（129×94）
python tools/art/design_nomsy_poses.py           # Codex 的姿势：换成定稿的颜色
python tools/lol/fx_ref_nomsy.py                 # 特效参考贴图（只在本地）
python tools/art/import_nomsy_fx.py              # 特效 -> tft_nomsy_fx / tft_nomsy_big，图标
python tools/art/rig_nomsy.py                    # 1 倍帧和 2.6 的原帧
python tools/art/ppu_restyle.py --hero nomsy     # 外描边
python tools/art/ppu_hd.py --hero nomsy          # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_nomsy  # 待机和选人卡片的小动作
python tools/art/preview_nomsy.py                # 预览和每个技能单独的 GIF
python tools/art/review_nomsy_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py      # 塞拉斯偷到的龙神飞升
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试
```
