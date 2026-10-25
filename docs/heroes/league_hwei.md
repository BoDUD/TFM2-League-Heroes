<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 彗 Hwei

<img src="img/league_hwei.png" alt="彗" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_hwei` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / CC |
| 高清帧 | PPU 1.5（画成 85%） |
| 附加包 | 无 |

![彗演示](../preview/league_hwei_showcase.gif)

其他预览：[逐帧预览](../preview/league_hwei_frames.png)、[特效表](../preview/league_hwei_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_hwei.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.53 秒 · 攻击距离 55000*

挥笔甩出一团墨。落款：技能命中英雄后4秒内再命中则引爆，造成45 + 35% 法强魔法伤害。主题：靖：画灾时加速25%，画悚时为自己和附近队友加护盾60 + 35% 法强。

### 技能1 · 主题：灾

*冷却 1 秒 · 施放距离 80000 · 施放：指定目标 · 敌人（不含防御塔）*

依局势作画：被控制的英雄头上落攒聚雷60 + 45% 法强，再加90 + 60% 法强；否则向英雄掷没骨火75 + 50% 法强加3%最大生命；没有英雄时画连皴山，熔岩灼烧并减速35%。均为魔法伤害。

### 技能2 · 主题：悚

*冷却 12 秒 · 施放距离 85000 · 施放：指定目标 · 敌方英雄*

依局势作画：贴身的英雄被阴沉变意恐惧1秒；否则轮流画滞涩幽瞳（睁眼后禁锢1.3秒）与双钩血喉（咬住并减速45%）。均造成80 + 50% 法强魔法伤害。

### 大招 · 焚心绚华绘

*冷却 35 秒 · 施放距离 80000 · 施放：指定目标 · 敌方英雄*

向英雄甩出颜料，命中后在其脚下展开画卷3秒，持续造成魔法伤害并减速25%，最后爆炸造成110 + 55% 法强魔法伤害。

### 数值

攻击力 70（每级 +6）、法强 40（每级 +20）、生命 940（每级 +94）、护甲 20（每级 +7）、魔抗 22（每级 +4）、移速 900（每级 +9）。

## 相关脚本和素材

- [`tools/kit/build_hwei.py`](../../tools/kit/build_hwei.py)
- [`tools/kit/setup_hwei.py`](../../tools/kit/setup_hwei.py)
- [`tools/lol/extract_hwei.py`](../../tools/lol/extract_hwei.py)
- [`tools/art/preview_hwei.py`](../../tools/art/preview_hwei.py)
- [`tools/art/rig_hwei.py`](../../tools/art/rig_hwei.py)
- [`assets/source/hwei/`](../../assets/source/hwei)

## 开发记录

> 下面是原来 README 里「英雄：彗」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中单（Magician，标签 AP / Magic / Range / CC），第 154 位英雄（G 组；计划里是下路替补，用户选了中路）。异画师 彗：墨绿色乱发的年轻画师，绿眼睛、耳坠，靛蓝画师外套配青绿翻领和金纹、橙色衬衫、棕色腰带、墨绿七分裤和青绿绑带，远侧脚踝一串粉色珠链，手里一支红蓝笔头的大画笔斜指地面，身后浮着一道弯月形的画痕（靛蓝底、金纹、橙红笔锋）和几滴颜料。技能方案 A（用户选）：主题：灾 / 主题：悚 / 焚心绚华绘，主题：靖并进被动；英雄联盟每个主题后面三选一，这里按局势替他挑，全部用技能数据做，没有附加包 |
| 普攻 / 被动 | 挥笔甩出一团墨（射程 55000，100% 攻击）。**落款**：技能打中英雄后 4 秒内再打中英雄，0.5 秒后炸开 45 + 35% 法强 魔法伤害（英雄联盟炸脚下一片；数据只能读彗自己身上的标记，所以炸的是第二下打中的那名英雄，一次施法只算一次）。**主题：靖**并进被动：每次画悚给自己 60 + 35% 法强 的护盾、身边 35000 内的友方英雄得到 85%（2 秒，渲浓），每次画灾移速 +25% 1 秒（飞染）。落款的印记挂满 4 秒（数据取不下敌人身上的标记，和薇古丝的暮气一样） |
| 技能1 | **主题：灾**（冷却 8 秒，射程 80000，对 `EnemyWithoutTower`，野怪兵线也打）按局势挑一种画：射程内有被控制的英雄 → **攒聚雷**：0.75 秒后雷劈在他头上，70 + 45% 法强，被控制再加 90 + 60% 法强（英雄联盟对不能移动的目标 2–2.75 倍）；否则射程内有英雄 → **没骨火**：火球 90 + 60% 法强 + 3% 最大生命；没有英雄（兵线、野怪）→ **连皴山**：熔岩落在目标处 35 + 25% 法强，留下半径 20000 的熔岩地 2.5 秒，每 0.5 秒灼烧 15 + 10% 法强、减速 35%。三种各有一套动作（`skill` / `skill_w` / `skill_e`） |
| 技能2 | **主题：悚**（冷却 12 秒，射程 85000，只对敌方英雄）按局势挑一种画，都是 80 + 50% 法强：英雄贴身（38000 内）→ **阴沉变意**：一张鬼脸飞过去，恐惧 1 秒（把贴上来的人吓跑）；否则 **滞涩幽瞳**（他头上睁眼 0.65 秒后禁锢 1.3 秒）和 **双钩血喉**（0.5 秒后咬住，定住 0.5 秒再减速 45% 1.5 秒；英雄联盟拉到嘴中间，这里改成原地咬住）轮流画。三种各有一套动作（`skill2` / `skill2_q` / `skill2_e`） |
| 大招 | **焚心绚华绘**（冷却 35 秒，射程 80000，只对敌方英雄）：甩出一团颜料直线飞出 100000，停在第一个英雄身上，在他脚下展开半径 25000 的画卷 3 秒，每 0.33 秒灼烧 12 + 8% 法强、减速 25%，最后炸开 220 + 100% 法强（英雄联盟 200–450 + 80% 法强、减速逐层叠加，中心目标死了会提前炸，数据读不到） |
| 连招 | 「有连招要做连招」：**悚 → 灾**：悚打中英雄（恐惧、禁锢、咬住）0.1 秒后，灾好了就对他放带控制加成的攒聚雷（游戏的 AI 按各自的冷却放技能，所以连招直接写在悚里）；**R → 灾**：画卷打中的第一个英雄 0.17 秒后，灾好了就掷没骨火。两下伤害技能打中英雄就引爆落款，所以每个连招都会落款再引爆 |
| 数值 | 攻击 70（+6）、法强 40（+20）、生命 940（+94）、护甲 20（+7）、魔抗 22（+4）、移速 900（+9）、射程 55000 |
| 平衡 | 经典引擎模拟（中路，对火法、冰法、雷法、风法、白法，两边三套阵容）：草稿 +1.90（种子 1-8，同一批对局妮蔻 +1.50）；追踪的对局里每种画法都出现（种子 3 / 5 / 7：攒聚雷每局 4–9 次、没骨火 5–15、连皴山 18–31，幽瞳和血喉各 9–14，落款引爆 21–38 次），只有阴沉变意三局一次，贴身距离 30000 → 38000 后 +1.44（种子 1-16）；禁锢取整到 1.3 秒、出手时间对好动作帧后定稿 +1.60（±0.32，种子 1-16） |
| 精灵图（高清帧 PPU 1.5） | Codex 第 0 步画了 A（四分之三侧面）和 SA（侧面），[`tools/art/design_hwei_hd.py`](../../tools/art/design_hwei_hd.py) 按各自的格子读回；用户选「头发顶到脚底 40 游戏像素，PPU 1.5，只做四分之三侧面」：60 行（连弯月画痕 75 行）。第 1 步两稿，用户选 A-1（62 × 76，[`tools/art/design_hwei_model.py`](../../tools/art/design_hwei_model.py)）。动作用户选「Codex 照骨架画姿势」（[`tools/art/pack_hwei_poses.py`](../../tools/art/pack_hwei_poses.py)，21 个姿势，英雄联盟那一帧按造型大小放在格子上当参考）：[`tools/art/design_hwei_poses.py`](../../tools/art/design_hwei_poses.py) 按头的大小读回、贴回定稿的头；Codex 的画笔画长了 1.1–1.5 倍，[`tools/art/brush_hwei.py`](../../tools/art/brush_hwei.py) 按定稿的画笔（握点到笔尖 26.5 格）在每个姿势的握点和方向上重画；13 个姿势的腿画成了大人的长腿、跑步两腿不交替，分两包只让 Codex 照短腿骨架重画腿（[`tools/art/pack_hwei_legs.py`](../../tools/art/pack_hwei_legs.py)），[`tools/art/design_hwei_legs.py`](../../tools/art/design_hwei_legs.py) 读回时上身一格不动地保留、只取新腿。[`tools/art/rig_hwei.py`](../../tools/art/rig_hwei.py) 照英雄联盟的节奏拼成 12 个动作（灾和悚的三种画法各一个），外套里读回时漏底的细缝用外套最深的靛蓝补上，死亡时画笔从手里掉下、落在一处不动。待机和选人卡片的小动作是普攻的举笔和滞涩幽瞳的高举。2026-10-22 用户：「画师局内有点大 可以调小一点」，局内缩到 **85%**（hd.rs SIZES，从 0.9、0.85、0.8 里选），帧往下挪 3 格让脚踩在地上，脸的位置 (3, -26) |
| 特效 | 24 张特效（[`tools/art/pack_hwei_fx.py`](../../tools/art/pack_hwei_fx.py) 的提示词，参考是英雄联盟里彗自己的贴图）：22 张用户让 Gemini 画的（JPG，没有透明），大招后补的两张里颜料团也是 Gemini 画的，画卷是 GPT 画的（用户：「慧还差一张 你写好提示词让gpt做吧」，4 × 4 的格子）。[`tools/art/process_hwei_fx.py`](../../tools/art/process_hwei_fx.py) 只按灰色边框的颜色抠底（他的靛蓝墨碰到格子边，按整张图抠会被抠掉）、按空隙切帧、把正面画的圆环压成地上的椭圆、做成对称（弹体上下对称，其余左右对称）；[`tools/art/import_hwei_fx.py`](../../tools/art/import_hwei_fx.py) 按技能放好：`league_hwei_fx` 18 张、`league_hwei_big` 6 张（落款引爆、攒聚雷、连皴山的熔岩、渲浓的水洼、画卷、画卷炸开） |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_hwei.py`](../../tools/lol/extract_hwei.py)）：普攻和命中、落款引爆，灾的三种（出手、爆炸、熔岩灼烧），悚的三种和命中，渲浓的护盾，大招的出手、命中、画卷展开和碎裂，三句台词 |
| 图标 | 官方技能图标（主题：灾、主题：悚、焚心绚华绘），从本地客户端取 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_hwei.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_hwei.py                      # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_hwei.py --face 3,-31         # 五种语言的文字、音效配置、共享文件里他的键（脸 3,-31）
python tools/art/design_hwei_hd.py                  # Codex 第 0 步的原图读回（A、SA）
python tools/art/design_hwei_model.py               # Codex 第 1 步的造型读回（A-1）
python tools/art/design_hwei_poses.py               # Codex 的姿势读回（贴回定稿的头、按定稿重画画笔）
python tools/art/design_hwei_legs.py                # 两包腿重画的读回，接回原来的上身
python tools/art/process_hwei_fx.py                 # Gemini / GPT 的特效图 -> 游戏尺寸（--src 放图的文件夹）
python tools/art/import_hwei_fx.py                  # 特效 -> league_hwei_fx / league_hwei_big
python tools/art/rig_hwei.py                        # 1 倍帧和 1.5 的原帧
python tools/art/ppu_restyle.py --hero hwei         # 外描边、脸的位置
python tools/art/ppu_hd.py --hero hwei              # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero hwei          # 待机和选人卡片的小动作
python tools/art/preview_hwei.py                    # 预览和演示 GIF
```
