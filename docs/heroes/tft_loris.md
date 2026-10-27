<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 洛里斯 Loris

<img src="img/tft_loris.png" alt="洛里斯" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_loris` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 辅助 |
| 分类 / 标签 | 功能型（Util） · AP / Magic / Melee / Tank / CC / Shield |
| 高清帧 | PPU 2 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_loris_skills.gif)、[逐帧预览](../preview/tft_loris_frames.png)、[特效表](../preview/tft_loris_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_loris.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.4 秒 · 攻击距离 25000*

举盾猛砸，造成100% 攻击力物理伤害。神盾使：每条命第一次生命低于75%和25%时，各获得最大生命12%的护盾（4秒）。

### 技能1 · 皮城争斗

*冷却 7 秒 · 施放距离 42000 · 施放：指定目标 · 敌人（不含防御塔）*

获得70 + 50% 法强的护盾（4秒），举盾冲锋，撞到的敌人受到110 + 70% 法强魔法伤害并晕眩1.5秒。

### 技能2 · 盾卫

*冷却 10 秒 · 施放距离 50000 · 施放：无目标 · 敌方英雄*

冲到附近生命比例最低的友方英雄身边，两人各获得70 + 45% 法强的护盾（4秒），期间替他承受30%的伤害。

### 大招 · 钢铁防线

*冷却 50 秒 · 施放距离 30000 · 施放：指定目标 · 敌方英雄*

把巨盾砸进地里，周围的敌人受到220 + 80% 法强魔法伤害、被击飞1秒并嘲讽2秒；自己受到的伤害降低50%（4秒）。

### 数值

攻击力 74（每级 +6）、法强 30（每级 +15）、生命 1250（每级 +115）、护甲 42（每级 +8）、魔抗 30（每级 +4）、移速 980（每级 +10）。

## 相关脚本和素材

- [`tools/kit/build_loris.py`](../../tools/kit/build_loris.py)
- [`tools/kit/setup_loris.py`](../../tools/kit/setup_loris.py)
- [`tools/lol/extract_loris.py`](../../tools/lol/extract_loris.py)
- [`tools/art/preview_loris.py`](../../tools/art/preview_loris.py)
- [`tools/art/rig_loris.py`](../../tools/art/rig_loris.py)
- [`assets/source/loris/`](../../assets/source/loris)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_loris`）的第六个英雄，辅助（Util，标签 AP / Magic / Melee / Tank / CC / Shield）。皮尔特沃夫拿巨型塔盾的大胡子执法官，金铲铲之战第 16 赛季的三费棋子（皮尔特沃夫 / 神盾使；第 13 赛季叫 TFT13_Beardy）。金铲铲里他只有一个技能「皮城争斗」（得盾、冲锋击退晕眩、然后嘲讽），所以拆成技能1（冲锋）和大招（嘲讽），技能2 和被动按辅助的保人设计，用户选了方案 A「神盾使·皮城争斗」。模型在 Riot 客户端的 `TFTSet16.wad.client`（`TFT16_Loris_16.skn`，两个子网格名字是空的：0 = 人、1 = 巨盾；九段动作只有路径哈希，按内容命名） |
| 普攻 / 被动 | 举盾猛砸（近战，100% 攻击）。**神盾使**：每条命第一次生命低于 75% 和低于 25% 时，各得一层最大生命 12% 的护盾 4 秒（tft.dll 的被动每拍看生命：数据读不到生命；一下掉过两条线就两层一起给） |
| 技能1 | **皮城争斗**（冷却 7 秒，施放距离 42000）：先得 70 + 50% 法强的护盾 4 秒，0.13 秒后举盾冲锋（RushTime 5000 × 10 拍），撞到的敌人受到 110 + 70% 法强魔法伤害、被撞开约 2 格、晕眩 1.5 秒。草稿里的大击退（2500 × 6）把被撞的人推出了队友的射程，模拟里一直是负的，只留一个看得出被撞开的小击退 |
| 技能2 | **盾卫**（冷却 10 秒，只在打英雄时放）：冲到 70000 以内生命比例最低的友方英雄身边（tft.dll 每拍走 4500，贴上去为止），两人各得 70 + 45% 法强的护盾 4 秒；那人这 4 秒受到的伤害少 30%，少掉的那部分由洛里斯承受（tft.dll 每拍把那人掉的血折回原伤害，从洛里斯身上扣，不会扣死）。身边没有队友就只给自己护盾 |
| 大招 | **钢铁防线**（冷却 50 秒，敌方英雄在 30000 以内时放）：双手把巨盾举过头顶，0.37 秒时砸进地里，36000 以内的敌人受到 220 + 80% 法强魔法伤害、击飞 1 秒、嘲讽 2 秒；他自己受到的伤害降低 50% 4 秒 |
| 数值 | 攻击 74（+6）、法强 30（+15）、生命 1250（+115）、护甲 42（+8）、魔抗 30（+4）、移速 980（+10），攻击间隔 1.4 秒（以布隆为参照） |
| 平衡 | 经典引擎模拟（辅助位，对牧师、武僧、吟游诗人、附魔师、道士，两边三套阵容，纯数据版：被动算成第一次出手时的固定护盾，盾卫随机挑队友）：草稿 −1.15（同一批 league_braum +1.52），只加伤害一直在 −1.2 ~ −1.7；去掉大击退 +0.33；加强控制（技能1 冷却 7 秒、晕眩 1.5 秒，大招冷却 50 秒、范围 36000、击飞 1 秒）后**定稿** +1.40 / +0.86（种子 1–8 / 9–16，league_braum +1.52 / +1.25）。去掉嘲讽是 −1.85，所以嘲讽保留 |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/loris.rs`](../../addons/tft/src/loris.rs)，和诺拉、拉露恩、希尔科、麦迪一起编成 `tft.dll`）：被动 `tft_loris:warden`（75% / 25% 的护盾、盾卫的分担伤害），技能2 `tft_loris:bulwark`（挑人）→ `tft_loris:leap`（每拍走一步、落地给盾）。`build_loris.py` 每次核对代码的默认参数、读写的名字和登记的效果都在数据里 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 | 他的大招本来就是纯数据，塞拉斯直接偷（特效表复制进附加包；`sylas_steal_check.py` 模拟里砸地和击飞的特效 10 次）。佛耶戈 / 妮蔻的表（辅助类）和俄洛伊的幽灵图（178 个）都加上了他 |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（巨盾立在身前，金铲铲的待机）和 B（持盾在身侧），实际格子约 11.2 px，人画得比要求大（约 75 格高），[`tools/art/design_loris_hd.py`](../../tools/art/design_loris_hd.py) 按它自己的格子读回；用户定 **B-1、高 42、PPU 2.0**（[`tools/art/design_loris_model.py`](../../tools/art/design_loris_model.py)：50×84，补上远处那只眼睛）。姿势包的骨架是他自己的动作按帧投影出来的（[`tools/art/pack_loris_poses.py`](../../tools/art/pack_loris_poses.py)：头放大 2 倍，巨盾画成金色轮廓、上端标金圈；冲锋和举盾那几帧模型转向镜头，换成 70° 视角；死亡动画把盾甩得很远，参考图里藏掉）。Codex 画了 16 个姿势，在定稿的 12 px 格子上、但用自己的一千多种颜色，身体比定稿大 4–8%：[`tools/art/design_loris_poses.py`](../../tools/art/design_loris_poses.py) 把颜色换回定稿的 35 种、每帧缩回定稿的大小、贴回定稿的头（趴在地上那帧头放倒、脸朝上）；[`tools/art/rig_loris.py`](../../tools/art/rig_loris.py) 按 Codex 在格子上画的位置摆放，拼成普攻（提盾 → 抡盾出拳 → 收势）、技能1（举盾 → 冲锋 → 收势）、技能2（冲刺 → 立盾）、大招（举盾过头 → 砸地）、受击、阵亡（后仰 → 跪地 → 趴下）。**跑步**：Codex 的四帧跑步盾后那条腿一直不动（用户：「怎么感觉在滑步」「左脚看起来完全不动吧」），改成布隆 / 泰坦的走法：定稿自己的两条腿轮流抬起、往前迈，身体随之起伏，8 帧 |
| 特效 | 13 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_loris_fx.py`](../../tools/art/pack_loris_fx.py) 的提示词，参考是金铲铲里他自己的粒子贴图 [`tools/lol/fx_ref_loris.py`](../../tools/lol/fx_ref_loris.py)），全部左右对称。[`tools/art/import_loris_fx.py`](../../tools/art/import_loris_fx.py) 切成 `tft_loris_fx` / `tft_loris_big`；盾卫的盾牌标记和嘲讽的愤怒标记原本盖在脸上，挪到头顶；大招的冲击波 Codex 只画了一条细线，导入时补画一圈向外扩散的铜色冲击环（内圈青蓝）和地裂纹，保留它的尘土碎石 |
| 音效 | 他自己的第 16 赛季金铲铲音效（Riot 客户端 Map22 的 `MODE_TFT_Set16_Champs_SFX`：盾击、命中、重击、施法、冲锋），护盾激活和冲击波只在第 13 赛季的包里（同一个模型，叫 TFT13_Beardy），大招配他的英文语音（WeGame 没有第 16 赛季的中文语音）；盾卫落地和大招的地裂借布隆的「挺身而出」落地和「冰川裂隙」命中（[`tools/lol/extract_loris.py`](../../tools/lol/extract_loris.py)，12 段） |
| 选人卡片 | 头顶到脚底 42 游戏像素：`banpick_center` −4（bp_card_audit 的规则：lo_idle 在中心上方 34.7），不另设缩放。脸 (1, −36)。待机按 `tools/art/hero_reels.py` 剪进立盾和提盾的帧，卡片轮播普攻、大招、技能2、技能1 |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_loris.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_loris.py                  # 技能数据（调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_loris.py                  # 五种语言的文字、音效配置、tft 包共享文件里他的键
python tools/art/design_loris_hd.py              # Codex 第 0 步的原图读回
python tools/art/design_loris_model.py           # 定稿 B-1 缩到 84 行，补远处的眼睛
python tools/art/design_loris_poses.py           # Codex 的姿势（定稿的颜色、大小和头）
python tools/art/import_loris_fx.py              # 特效 -> tft_loris_fx / tft_loris_big，图标
python tools/art/rig_loris.py                    # 1 倍帧和 2.0 的原帧（跑步是布隆的走法）
python tools/art/ppu_restyle.py --hero loris     # 外描边
python tools/art/ppu_hd.py --hero loris          # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero loris      # 待机和选人卡片的小动作
python tools/art/preview_loris.py                # 预览和每个技能单独的 GIF
python tools/art/review_loris_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py      # 塞拉斯偷到的钢铁防线
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试（洛里斯、麦迪、希尔科、拉露恩、诺拉）
```
