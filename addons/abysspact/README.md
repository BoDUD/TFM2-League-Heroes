# abysspact (`abysspact.dll`)

**Abyss Pact · 渊契**（`abysspact`）独立暗黑奇幻原创英雄包的原生 DLL，随 `abysspact/` 一起由 `tools/package_mod.py --src abysspact` 编译并打包安装。

## 包含内容

- **高清帧引擎（`hd.rs`）**：通过 `hd_engine` 登记 5 位渊契英雄（PPU `2.75`）、骷髅兵召唤单位（`abysspact_skeleton`，PPU `2.75`）与 5 套特效图集（FX PPU `3.3`）。
- **断誓 `abysspact_oathbreaker`（`oathbreaker.rs`）**：施放技能扣除 6% 当前生命（永不致死）；每损 10% 血获得 +4% 攻击 / +5% 攻速并切换三档血誓紫火（`oath_low/mid/high`）；大招 6 秒不死期间参与击杀结束回复 25% 最大生命，否则再烧 15% 当前生命。
- **无面 `abysspact_faceless`（`faceless.rs` + `faceless_view.rs`）**：大招对 25% 血以下敌方英雄触发真实斩杀；参与击杀即触发 10 秒「夺面」——模拟层切换目标定位套件与借用大招，显示层通过 `game_places` 挂钩实时将模型整身替换为被杀英雄（支持全库 306+ 英雄）。
- **呓语 `abysspact_whisperer`（`whisperer.rs`）**：逐目标追踪疯狂层数（1–3 层头顶浮标 `madness_1..3`），满 3 层触发 1.5 秒恐惧、15k 范围法伤爆炸并向周围友军传染 +1 层疯狂，形成连锁发狂。
- **骸弦 `abysspact_bonebow`（`bonebow.rs`）**：通过 `spawn_unit` 生成真实可走、可砍、可扛伤的 `abysspact_skeleton` 骷髅兵（第 4 箭 / Q 穿透拉起，上限 3 只活 6 秒；R 箭雨额外拉起 5 只活 8 秒）；W 葬礼令全军冲向目标自爆减速。
- **鸦医 `abysspact_corvus`（`corvus.rs`）**：疫病每秒造成 2% 最大生命法伤并自动传染 15k 内最近未染病敌人；队友靠近 20k 内染病敌人每秒回 1% 最大生命（最多叠加 3 名病人）；W 渡鸦停栖队友肩头每秒啄敌挂疫病。

## 版本

- `0.1.0`：渊契第一批 5 位英雄（断誓、无面、呓语、骸弦、鸦医）及 2 套召唤物（骷髅兵、渡鸦）。
