<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 卡特琳娜 Katarina

<img src="img/league_katarina.png" alt="卡特琳娜" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_katarina` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 刺客（Assassin） · AP / Magic / Melee |
| 高清帧 | PPU 1.5 |
| 附加包 | [卡特琳娜附加包](#附加包)（`league_katarina`）、[游戏 AI 不按的技能替它按](#附加包)（`league_ult_press`） |

![卡特琳娜演示](../preview/league_katarina_showcase.gif)

其他预览：[逐帧预览](../preview/league_katarina_frames.png)、[特效表](../preview/league_katarina_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_katarina.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 0.92 秒 · 攻击距离 23000*

贪婪：被她伤害过的敌方英雄3秒内阵亡时，Q、W冷却刷新，瞬步就绪。落地的匕首留4秒，捡起时旋斩周围敌人，造成138+100% 法强魔法伤害，瞬步冷却降为2秒。

### 技能1 · 弹射之刃

*冷却 8 秒 · 施放距离 62500 · 施放：指定目标 · 敌人（不含防御塔）*

掷出弹射之刃，造成150+62% 法强魔法伤害，再弹向附近2个敌人；匕首落在第一个目标身后。瞬步就绪且匕首旁有敌方英雄时，瞬步到匕首处。

### 技能2 · 伺机待发

*冷却 11 秒 · 施放距离 55000 · 施放：指定目标 · 刚交过手的敌方英雄*

瞬步就绪时先瞬步到敌方英雄身边，造成75+38% 法强魔法伤害（冷却10秒）；再把匕首抛向空中，1.25秒后落地，获得逐渐衰减的移速+60%。

### 大招 · 死亡莲华

*冷却 60 秒 · 施放距离 30000 · 施放：指定目标 · 敌方英雄*

原地旋转引导2.5秒，向周围的敌方英雄连续掷出匕首，共造成650+350% 法强魔法伤害并使其治疗效果-60%。受到控制时中断。

### 数值

攻击力 112（每级 +13）、法强 40（每级 +26）、生命 1020（每级 +92）、护甲 32（每级 +8）、魔抗 24（每级 +4）、移速 1100（每级 +13）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 卡特琳娜附加包

[卡特琳娜附加包](../../addons/league_katarina/README.md)：`league_katarina` v0.1.0

|  | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 瞬步 | 只在 Q（跳到这把 Q 落地的匕首）和 W（先切到目标英雄身边）里用 | 另外**瞬步一好就自己判断**：射程内哪把匕首旁有敌方英雄就跳过去（那里生命比例最低的英雄优先），落地捡刀旋斩、冷却缩短，接着跳下一把——**匕首循环**；生命低于 30% 而身边有敌方英雄时，跳到离敌人最远的那把匕首撤离；匕首旁 3 名以上敌方英雄、她生命又不到 60% 时不跳进人堆 |
| 贪婪 | 被她伤过的英雄 3 秒内阵亡，Q、W 刷新、瞬步就绪；一个窗口里只认一次 | **她参与的每一次英雄击杀**（击杀或助攻）都刷新，几个人同时阵亡各算一次 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】贪婪：她参与击杀的每个敌方英雄都让Q、W冷却刷新、瞬步就绪。瞬步就绪时自己跳到有敌人的匕首旁（残血时跳到远离敌人的）。捡起匕首旋斩周围敌人，造成138+100% 法强魔法伤害，瞬步冷却降为2秒。

### 游戏 AI 不按的技能替它按

[游戏 AI 不按的技能替它按](../../addons/league_ult_press/README.md)：`league_ult_press` v0.5.5（通用附加包，下面只列和卡特琳娜有关的部分）

|  | 装了附加包，什么时候按 |
|---|---|
| 劫 W、格温 E、佛耶戈 E、卡特琳娜 W（冲上去的） | 他生命 **≥ 40%**；射程内（劫 55000、格温 45000、佛耶戈 46000、卡特琳娜 55000，引擎只接最近被我方打过的）的敌方英雄，**不在敌方塔下**（75000 内；生命 25% 以下的除外）、**目标身边 60000 内的敌方英雄不比他身边的我方英雄（含他）多**，挑**生命比例最低**的。劫还要 **Q 好着**（主包标记 `league_zed_q_cd` 不在，W-E-Q 一起出手，主包最初的设计）。AI 正往远处撤（走路目的地比现在离目标远 10000 以上）时不按 |
| 卡特琳娜 R | 她生命 ≥ 30%、自己不在敌方塔下（目标残血除外）；25000 内的敌方英雄，身边 50000 内有**两个以上**，或目标生命**不到一半** |

## 相关脚本和素材

- [`tools/kit/build_katarina.py`](../../tools/kit/build_katarina.py)
- [`tools/kit/setup_katarina.py`](../../tools/kit/setup_katarina.py)
- [`tools/lol/extract_katarina.py`](../../tools/lol/extract_katarina.py)
- [`tools/art/preview_katarina.py`](../../tools/art/preview_katarina.py)
- [`tools/art/rig_katarina.py`](../../tools/art/rig_katarina.py)
- [`assets/source/katarina/`](../../assets/source/katarina)

## 开发记录

> 下面是原来 README 里「英雄：卡特琳娜」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中单（Assassin，标签 AP / Magic / Melee），第 108 位英雄。不祥之刃 卡特琳娜（客户端里名字和称号是反着的，按官方）：近战 AP 刺客，飞刀、瞬步、捡匕首旋斩、死亡莲华。用户的选择（全按推荐）：中单 AP 刺客；技能 1 = Q 弹射之刃（瞬步就绪时接瞬步跳到落地的匕首），技能 2 = W 伺机待发（瞬步就绪时先瞬步切入），E 瞬步不占技能位、冷却记在她身上（崔丝塔娜 W 的做法，两个技能位都不会空放）；附加包要；职业连招开；高清 PPU 1.5，看过脸后改成 1.79，又嫌太高清改回 1.5 |
| 普攻 / 被动 | 匕首刺击（近战，攻击距离 23000，攻击间隔 55 tick，第 8 tick 刺中，物理）。「贪婪」：被她伤害过的敌方英雄 3 秒内阵亡（不管是谁杀的），Q、W 冷却刷新、瞬步就绪（佛耶戈的击杀窗口：同一个窗口只认一次）。**匕首**：Q、W 的匕首落地后留 4 秒，她走到 9000 内就捡起来，原地旋斩一圈（半径 30000，138 + 100% 法强魔法），瞬步冷却降为 2 秒；地上最多同时 3 把（奥拉夫捡斧的做法）。旋斩的效果挂在她每次出手时挂上的周期效果里，Q、W 两棵每 tick 复制的技能树只放一个标记 |
| 技能1 | Q「弹射之刃」：冷却 480 tick，对 62500 内的敌人放（小兵、野怪也打）。第 8 tick 掷出旋转的匕首，150 + 62% 法强魔法，再弹向附近 2 个敌人（随机挑，可能再打到同一个）；匕首从第一个目标身上弹起，40 tick 后落在他被打中时站的地方（数据里投射物都从她身上出发，算不出英雄联盟的「目标身后 350 码」）。瞬步就绪、匕首旁有敌人时，刀一落地她就瞬步过去捡刀旋斩（Q-E） |
| 技能2 | W「伺机待发」：冷却 660 tick，只对 55000 内**正在交战的**敌方英雄放（`EnemyChampionRecentlyAttacked`：对任何英雄都放时她常一个人跳进敌阵，模拟里差 0.7 个击杀差）。瞬步就绪时先瞬步到他身上（75 + 38% 法强魔法，瞬步冷却 600 tick），再把匕首抛向空中，75 tick 后落在抛刀的地方，移速 +60% 分三段衰减（E-W） |
| 大招 | R「死亡莲华」：冷却 3600 tick，30000 内有敌方英雄时放。原地旋转引导 150 tick，每 10 tick 向半径 50000 内每个敌方英雄掷一把匕首：共 650 + 350% 法强魔法，重伤（治疗 −60%，3 秒）。被控就断（玛尔扎哈大招的做法）；连续两跳圈里都没有英雄也提前收招（模拟里大多数大招只掷了 1–9 把刀：她在圈边开大，对面几步就走出去了，她还站着空转） |
| 高手连招 | Q→E 跳刀捡刀旋斩；E→W 切入抛刀、刀落脚下再旋斩；贪婪刷新后接着对下一个英雄 E-W / Q；大招只在近身时放 |
| 附加包 | 可选的附加包 [`addons/league_katarina`](../../addons/league_katarina/README.md)（在附加包合集里，原生代码，主包不装它也完整）：**智能瞬步**——瞬步一好就自己判断，射程内哪把匕首旁有敌方英雄就跳过去（那里生命比例最低的英雄优先），落地捡刀旋斩、冷却缩短，接着跳下一把（匕首循环）；残血时跳到离敌人最远的匕首撤离；不在残血时跳进 3 人以上的人堆。**贪婪按每次击杀 / 助攻**刷新，几个人同时阵亡各算一次。大招只打最近 3 个英雄、Q 精确落在目标身后 350 码这两条原生代码改不了数据，没有做（见附加包说明）。日志 `league_katarina.log`。还没在游戏里看过日志 |
| 附加包（替 AI 按） | 可选的附加包 [`addons/league_ult_press`](../../addons/league_ult_press/README.md)（在附加包合集里，原生代码，主包不装它也完整）：游戏 0.6.4 的 AI 很少按她的 R 和 W（只读观察包：每 10 分钟 1.5 次和 4.2 次，102 局）。附加包按局面替 AI 按（用户：「有问题的英雄全部改成rust」）：R——她生命不低于 30%、自己不在敌方塔下（目标残血除外），25000 内有敌方英雄，而且身边 50000 内两个以上或那人生命不到一半；W——她生命不低于 40%，55000 内最近被我方打过、不在敌方塔下、身边不比她人多的敌方英雄里挑生命比例最低的；AI 正往远处撤时不按 W |
| 数值 | 攻击 112（+13）、法强 40（+26）、生命 1020（+92）、护甲 32（+8）、魔抗 24（+4）、移速 1100（+13） |
| 平衡 | 中路对五个基础法师，三套阵容、两边各打，10 分钟经典引擎模拟：定稿 k2 种子 1–12 +1.49、13–24 +1.12（同一批种子泰隆 +1.22；同组中单 +1.0..+1.7）。草案 −2.88；改掉 Q 匕首远落、大招圈边空转、W+E 乱切之后在 0 附近，单加生命、缩冷却、大招伤害都推不动，全部技能伤害 ×1.5 是 +3.25、×1.2 +0.15，定在 ×1.25（试过的几组在 `tools/kit/build_katarina.py` 的注释里）。Q-E 改成只对英雄之后（用户：「卡特琳娜出现乱移动的情况 查一下 打蚂蚱的时候」：匕首旁有野怪、小兵她也瞬步，在野怪堆里来回闪）：种子 1–12 +0.94、13–24 +1.76，两批平均和原来差不多 |
| 精灵图（高清帧 PPU 1.5） | Codex 第 0 步画了两张原画，用户选 K1、头顶到鞋底 38 个游戏行；第 1 步 Codex 用画图模型按 K1 的密度画了两稿 3/4 侧身，用户选侧身 1。[`tools/art/design_katarina_hd.py`](../../tools/art/design_katarina_hd.py) 按各自的格子读回（K1 约 12 px 一格、侧身约 11 px）、侧身缩到 K1 的 68 行、统一 40 色，K1 的头贴到侧身上（只换头发、皮肤、眼睛，背后的刀柄留着）。Codex 照英雄联盟的骨架（[`tools/lol/native_pose.py`](../../tools/lol/native_pose.py)，60°）画了 42 帧动作（跑步 8、普攻 5、Q 5、W 5、瞬步落地 3、捡刀旋斩 4、大招循环 6、死亡 6；第 4 帧后生图额度用完，换账号续画），每帧贴的都是造型那颗头。[`tools/art/rig_katarina.py`](../../tools/art/rig_katarina.py) 读回、待机呼吸、受击闪白，`ppu_restyle.py` 加一格描边。起初按 PPU 1.5 缩小（同一颗头只缩一次），用户看了脸：「脸部用PPU调清晰点吧」——缩小把绿眼睛和眼上的疤缩没了，改成造型自己的密度 1.79（68 格 ÷ 38 游戏行），帧不再缩放。进游戏后用户：「卡特琳娜太高清了 降低点像素」——同样的游戏大小下把 1.79 / 1.6 / 1.5 / 1.4 并排给用户看，选了 1.5（`rig_katarina.py` 从造型的密度缩到 1.5，同一颗头只缩一次） |
| 特效 | Codex 第 3 步的 18 个特效 + 3 张画进帧的图（`assets/source/katarina/codex_fx`）。[`tools/art/import_katarina_fx.py`](../../tools/art/import_katarina_fx.py)：Codex 第 3 步的交付没到这台电脑上，用户：「特效你自己处理啊 我发了那么多图给你了」——用户贴在对话里的交付图存进 `assets/source/katarina/codex_fx/pasted`，[`tools/art/regrid_katarina_fx.py`](../../tools/art/regrid_katarina_fx.py) 按提示词的格子读回成游戏格子（`pixel_1x` + `manifest.json`）：13 张单独贴的图按整张图的宽和每格多少格算，只在文件总览里出现的旋转飞刀、捡刀旋斩、死亡莲华、W 加速、重伤 5 张按帧距算、只取不透明的芯；每格取它的像素均值往最亮的四分之一推、归到那张特效的色阶；要对称的逐格对称，旋斩和莲华中间给她的身体留空。3 张画进帧的刀光只在总览里有小图，按原位放刺击会斜穿过她全身，改成按提示词的长度、尖端对准定位图的青色十字。[`tools/art/import_katarina_fx.py`](../../tools/art/import_katarina_fx.py) 写成 `league_katarina_fx`（飞刀、匕首、打中、瞬步的烟、抛刀、地上的匕首、贪婪刷新、加速、重伤）和 `league_katarina_big`（旋斩、死亡莲华），`rig_katarina.py --pinholes` 把刀光叠进普攻第 3 帧、Q 第 3 帧、瞬步第 2 帧 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_katarina.py`](../../tools/lol/extract_katarina.py)，16 段）：刺击出手 / 打中、Q 出手 / 飞刀 / 打中 / 匕首弹起 / 落地、W 抛刀、E 瞬步、捡刀旋斩、贪婪刷新、R 死亡莲华，配音 Q / W / E / R（E 没有自己的配音，用 Q / W 那一组里的另一句） |
| 图标 | 官方技能图标（Q 弹射之刃 / W 伺机待发 / R 死亡莲华，另有 E 瞬步、被动贪婪、匕首旋斩），从本地客户端取 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_elise.py
python tools/kit/build_elise.py                    # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_elise.py --face 0,-37 --banpick -3   # 五种语言的文字、音效配置、共享文件里她的键
python tools/art/design_elise_hd.py                # Codex 的原画读回成两张造型
python tools/art/import_elise_strips.py            # Codex 的 65 帧动作：比例拉回、贴造型的头
python tools/art/import_elise_run.py <交付>/elise-run   # 人形跑步：Codex 重画的腿 + 造型的上半身（读 raw/ 原稿，原稿不进仓库，仓库留 codex_run/ 的 1 倍稿）
python tools/art/rig_elise.py                      # PPU 1.8 的帧和 1 倍图
python tools/art/ppu_restyle.py --hero elise       # 描边
python tools/art/ppu_hd.py --hero elise            # hd_ / lo_ 帧
python tools/art/import_elise_fx.py                # 特效
python tools/art/preview_elise.py                  # 预览和演示 GIF
python addons/league_elise/make_override.py        # 附加包的副本（主包的伊莉丝改了就重跑）
```

美术提示词见 [`assets/source/elise/`](../../assets/source/elise) 里的 `PICTURE_PROMPT.md`、`MODEL_STRIPS.md`、`RUN_PROMPT.md`、`PROMPTS_FX.md`；Codex 的交付在 `codex_picture/`、`codex_strips/`、`codex_run/`、`codex_fx/`。

逐帧预览：[`docs/preview/league_elise_frames.png`](../preview/league_elise_frames.png?v=1015a)，特效：[`docs/preview/league_elise_effects.png`](../preview/league_elise_effects.png?v=1015a)。
python tools/lol/extract_katarina.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_katarina.py                 # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_katarina.py                 # 五种语言的文字、音效配置、共享文件里她的键
python tools/art/design_katarina_hd.py             # Codex 的原画和侧身读回成两张造型
python tools/art/rig_katarina.py                   # 1 倍帧和 1.5 的高清帧（--prepare 读 Codex 的交付）
python tools/art/ppu_restyle.py --hero katarina    # 描边
python tools/art/regrid_katarina_fx.py            # 贴图读回成游戏格子
python tools/art/import_katarina_fx.py             # 特效和画进帧的图
python tools/art/rig_katarina.py --pinholes        # 补小洞、叠上画进帧的图
python tools/art/ppu_hd.py --hero katarina         # hd_ / lo_ 帧
python tools/art/preview_katarina.py               # 预览和演示 GIF
python addons/league_katarina/make_override.py     # 附加包的副本（主包的卡特琳娜改了就重跑）
```

美术提示词见 [`assets/source/katarina/`](../../assets/source/katarina) 里的 `PICTURE_PROMPT.md`、`MODEL_PROMPTS.md`、`MODEL_STRIPS.md`、`PROMPTS_FX.md`；Codex 的交付在 `codex_picture/`、`codex_side/`、`codex_strips/`、`codex_fx/`。

逐帧预览：[`docs/preview/league_katarina_frames.png`](../preview/league_katarina_frames.png?v=1015b)，特效：[`docs/preview/league_katarina_effects.png`](../preview/league_katarina_effects.png?v=1015b)。
