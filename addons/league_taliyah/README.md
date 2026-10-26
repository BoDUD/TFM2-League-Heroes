# 塔莉垭附加包（`league_taliyah`）

用户（2026-10-24）：「技能对了，继续接入（音效、文字、注册、扩展包）」。

主包的塔莉垭是纯数据：数据造不出挡路的东西，墙幔的两种墙都只是区域。这个附加包把墙做成英雄联盟那样的真地形：

| 墙 | 主包（纯数据） | 附加包 |
|---|---|---|
| 竖墙（敌人近、或她已在打架） | 目标处一片竖长方形区域：立起时站在上面的敌人被拖到她那一侧，之后碰到的敌人减速 `r_slow`%（卡在墙边） | 同一块地方是真的墙：英雄、小兵、野怪、召唤物（两边都算，她自己也算）都过不去；立起时压在上面的单位推到她那一侧 |
| 横墙（敌人远：骑墙） | 从她脚下朝目标铺 `r_n` 段横长方形区域，碰到的敌人减速 | 每一段都是真的墙；她骑墙时站在墙顶上不受挡，跳下来那一 tick 推到近的一侧 |

英雄联盟里塔莉垭的被动「浮石冲」是贴着地形时加移速；两边都没做：引擎接口读不到地图上的墙。

**脱战骑石头**（0.2.0，用户 2026-10-26：「塔利亚怎么是飞着走路的 不对吧」，选「像英雄联盟」）：主包的移动动画 `run` 是用脚跑（Codex 画的 4 帧，照英雄联盟的 Run1），踩石冲浪是另一套 `surf`。游戏按名字自动播 `run`，数据换不了；本包的 `src/view.rs`（照克烈的下马换动画）在她没在打架（身上没有 `league_taliyah_fight`）或刚放完墙幔（`league_taliyah_r_surf`）时把 `run` 换成 `surf`，打起来换回来。复活后从泉水出来也是骑石头。日志里每个塔莉垭状态一变就记一行 `SURFING` / `on foot`。需要主包 0.234.0 以上（图里有 `surf`）。

## 怎么接上的

`mod.override_info` 把主包的塔莉垭换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_taliyah.py` 的 `native=1` 生成）：

- 墙不再减速、不再拖人（区域还在，横墙的区域只当找位置用）；
- 立竖墙那一刻她身上挂 3 tick 的 `league_taliyah_wall_up`、开始铺横墙那一刻挂 `league_taliyah_lay_up`，同时给墙幔的目标挂 3 tick 的 `league_taliyah_aim`；
- `passive` 是本包的 `league_taliyah:wall`，参数 `r_t`、`r_w`、`r_h`、`r_seg`、`r_n`、`r_lay_speed` 来自主包参数表 P：
  - `wall_up` 刚出现：带 `aim` 的敌方英雄站的地方就是竖墙的中心（宽 `r_w`、高 `r_h`，立 `r_t` tick）；
  - `lay_up` 刚出现：从她脚下朝带 `aim` 的英雄，第 k 段在 k×`r_seg` 处，按铺墙的线的速度算出哪一 tick 铺下；那几 tick 里她新放出、停着不动的区域离算的位置不远就对上去（线停在哪由引擎定），对不上的晚 3 tick 按算的位置立；
  - 墙立着时，每个单位的中心一进墙（长方形四边各加单位半径）就退回上一 tick 的位置，但保留顺着墙走的那一半（竖墙保留上下、横墙保留左右），绕墙走不会被粘住；她身上有 `league_taliyah_riding`（骑墙）时不挡她。
- 大招的说明换成附加包自己的文字（`description.league_taliyah_addon.ult`，写着「墙是真的地形」），游戏里看说明就知道副本有没有生效。

状态都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_taliyah`：单元测试（参数、进墙退回只留顺墙的一半、立墙时推出去、横墙每段的位置和铺下的 tick、只认停着不动的新区域）。
- 主包的塔莉垭改了以后重新跑 `python addons/league_taliyah/make_override.py`（它先核对主包的 `league_taliyah.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只比较不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_taliyah.log`：`SPAWN`、立竖墙 `UPRIGHT`、开始铺横墙 `LAY`、每一段 `STRETCH`（`zone` 是对上了区域，`worked out` 是按算的位置）、挡住 `HOLD`、推出去 `PUSH`；找不到目标时 `UPRIGHT?` / `LAY?`。
