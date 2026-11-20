# ragnarok 包的代码（`ragnarok.dll`）

ragnarok 包（mod_id `ragnarok`，源文件在 [`ragnarok/`](../../ragnarok/)）是原生 mod：终末的女武神（Record of Ragnarok）的角色，数据做不到的地方写在这个 crate 里，编成 `ragnarok.dll` 跟着包一起装（`python tools/package_mod.py --src ragnarok ...` 会编好带上）。和金铲铲包一样，一个英雄一个模块；新英雄在 `src/` 加模块，在 `src/lib.rs` 的 `init` 里调用它的 `register`。

第一个英雄是吕布奉先（2026-11-20，用户：「codex/ragnarok-lubu-assets-v02 开始做新的mod了 codex完成了部分美术了 技能代码逻辑之类的都需要你来做」）。美术、图标、音频是 Codex 做的（[`assets/source/lubu/`](../../assets/source/lubu/README.md)），技能、数据、原生代码、高清帧接入和平衡是这里做的。

**高清帧**：[`src/hd.rs`](src/hd.rs) 是本包的高清帧表，`init` 先把它交给三个包共用的 [`hd_engine`](../hd_engine/src/lib.rs)：游戏里第一个加载的包 DLL 自己挂钩，后加载的把表交给它（[`share.rs`](../hd_engine/src/share.rs)），所以只开本包也有高清帧，和英雄联盟、金铲铲包一起开也不抢。吕布、索尔的高清帧就是 Codex 的原画（128 格；吕布 PPU 1.94、索尔 1.65，两人头顶一样高），1 倍帧是从它缩出来的后备；他们打在别人身上的特效图（火花、天喰冲击、碎盾、雷击、落锤冲击、雷槌觉醒）也是高清的（`EFFECTS` / `DRAWN_EFFECTS`，都是 1.65）。引擎的日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\ragnarok.log`。

| 英雄 | 模块 | 做什么 |
|---|---|---|
| 吕布奉先 `ragnarok_lubu` | [`src/lubu.rs`](src/lubu.rs) | 被动「盾牌破坏者」、配音 |
| 索尔 `ragnarok_thor` | [`src/thor.rs`](src/thor.rs) | 配音、倒地声（技能全在数据里） |

## 吕布奉先

数据：[`tools/kit/build_lubu.py`](../../tools/kit/build_lubu.py)（参数表 P，数值是 10 分钟经典引擎模拟调出来的，见文件头），文本和音效：[`tools/kit/setup_lubu.py`](../../tools/kit/setup_lubu.py)，图：[`tools/art/import_lubu.py`](../../tools/art/import_lubu.py)。

| 技能 | 做法 |
|---|---|
| 普攻 | 方天画戟重击，单体 100% 攻击力物理伤害 |
| 横扫（Q） | 第 0.42 秒戟扫前方扇形（半径 38000、左右各约 66°），50 + 130% 物理伤害、减速 40% 1.5 秒 |
| 破阵（E） | 第 0.34 秒朝目标冲 35200 单位、穿过去（引擎自己的冲刺，墙照样挡），路上的敌人 40 + 100% 物理伤害、击飞 0.6 秒 |
| 天喰（R） | 举戟蓄力 1.2 秒（不受控制、受到的伤害降低 30%），然后朝目标斩一刀：75000 长的一条线上的敌人 200 + 280% 物理伤害、眩晕 0.8 秒。一刀，不是持续激光；蓄力时被打死就不斩 |
| 被动 盾牌破坏者 | 下表 |

被动 `ragnarok_lubu:breaker`（参数 `p_pen` / `p_shield` / `p_break` 从数据的 `passive.params` 来）：

- **无视护甲**：每条命一出来就挂 `ragnarok_lubu_p_pen`（护甲穿透 15%，永久）。
- **打盾加倍**：他每一下（普攻和技能，`on_attack`）打到带护盾的敌人，对护盾多算 100%：只加到刚好打掉护盾为止，碎了以后的部分照常打血，不会越过护盾多打（护盾 s、这一下 d：加 min(d, s/2)）。
- **真的打碎才算**：下一拍再读目标的护盾，确实是 0 才算打碎：播碎盾的画面和声音，补 30% 攻击力的物理伤害。没碎就不播，日志记一行 `HELD`。
- **配音**：关智一的原声十句里，一局第一次和敌方英雄交手说「呂布の戦、しかと見届けよ」，杀英雄轮流说三句，复活说「この呂布奉先」，放破阵时三成概率说一句；每类有自己的冷却，任意两句至少隔 8 秒。天喰蓄力那句「全身全霊」是数据自己放的。

经典引擎跑不了原生代码，平衡模拟用 `build_lubu.py --plain`（护甲穿透改成第一个技能挂上，没有护盾那部分）。

## 索尔

数据：[`tools/kit/build_thor.py`](../../tools/kit/build_thor.py)（参数表 P，数值是 10 分钟经典引擎模拟调出来的，见文件头），文本和音效：[`tools/kit/setup_thor.py`](../../tools/kit/setup_thor.py)，图：[`tools/art/import_thor.py`](../../tools/art/import_thor.py)。

| 技能 | 做法 |
|---|---|
| 普攻 | 雷槌重击，单体 100% 攻击力物理伤害 |
| 雷神之锤（Q） | 第 0.43 秒砸地，前方 14000 处半径 26000 内的敌人 60 + 70% 攻击力 + 4% 最大生命物理伤害、眩晕 0.7 秒（觉醒时 1.1 秒） |
| 回旋雷槌（E） | 第 0.37 秒朝目标方向掷出雷槌，飞 44000 再飞回（league_sivir 的 Q 那样：去程到头接一个回到施法者的弹道），来回穿过的敌人 40 + 60% + 2% 最大生命物理伤害、减速 40% 1 秒。雷槌在外面时他空手站着（`skill2_wait`），真飞回来才接（`skill2_catch`）并得到 60 + 50% 攻击力的护盾 2.5 秒；最多等 0.67 秒 |
| 觉醒雷槌（R） | 雷槌立刻觉醒 8 秒，蓄力 1.25 秒（不受控制、受到的伤害降低 45%），然后前方 24000 处半径 44000 内的敌人 180 + 100% + 8% 最大生命物理伤害、击飞 1.5 秒；蓄力时被打死就不砸 |
| 被动 雷槌觉醒 | 每放三次技能（雷神之锤、回旋雷槌，觉醒时不算）雷槌觉醒 6 秒：红色裂纹和声音，普攻再加 25 + 3% 最大生命的魔法伤害，雷神之锤的眩晕变长。计数是数据里的施法者标记（t1 / t2） |

被动 `ragnarok_thor:voice` 只管声音（没有参数）：绿川光的原声十句，事件照 Codex 的 audio_events.json 分：一局第一次和敌方英雄交手说一句（三句里按拍数挑）、杀英雄两句轮流、雷槌觉醒时一半概率说「このミョルニルで」、复活三句轮流；每类有自己的冷却，任意两句至少隔 8 秒。大招那句「一撃のもとに」是数据放的，大招一放就当刚说过，大招带出来的觉醒不再叠一句。死的时候放 Codex 的倒地声（延迟 0.5 秒，对上死亡动作躺下）。

## 检查

- 在 `addons/` 下 `cargo test -p ragnarok`（CI 也跑）：吕布的被动参数、护盾加成的算式（碎和没碎两种情况下血量都等于「对盾双倍」应有的数）、护甲 buff；两人配音的冷却和轮换、每句都是 Codex 的十句之一（索尔的十句每句正好用一次）；`src/hd.rs` 的表（hd_ 帧正好是 1 倍帧的 PPU 倍、每个动作都有 hd_ / lo_ 帧、特效图有占位的 idle / hd_idle、表写成文本交给主再读回来一样）。
- `python tools/kit/build_lubu.py` 每次核对 `src/lubu.rs` 的默认参数和 P 一致、DLL 播的画面在数据里有。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\ragnarok_lubu.log`：`SPAWN`、打到带盾的人 `SHIELD`（打之前的护盾、这一下、加了多少）、碎了 `BREAK`、没碎 `HELD`、配音 `VOICE`。
