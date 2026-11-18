# 英雄联盟赛事（测试版 v0.0.1，单独的 mod）

用户 2026-11-18：「能不能做个赛事mod啊 现在比赛赛事不像英雄联盟 每年也太固定了」，选了三项：

1. 换成英雄联盟的名字；
2. 每年赛制会变；
3. 赛程日期和赛事每年浮动。

无畏征召不用做：新建生涯时的 BP 规则里本来就有「无畏」和「无畏（困难）」。

## 游戏原来的赛事

- **联赛**：6 个赛区（韩国、中国、欧洲、北美、南美、日本），各有一个一级、一个二级联赛，每个 10 支队伍。
  - 每年春季、夏季两个赛季，有季后赛和升降级赛。
  - 来源：`asset/base/setting/data_setting` 的 `leagues`。
- **国际赛**：4 个，都是小组赛加淘汰赛。
  - 东部 / 西部挑战者杯（`ChallengersEastern` / `ChallengersWestern`）、大师赛（`Masters`）、冠军赛（`Champions`）。
  - 来源：同一个文件的 `tournaments`。
- **全年日程**：每年一条 `YearSchedule` 记录，是一串（日期，事件）。
  - 事件有 13 种：`StartRecruit` / `EndRecruit`、`LeagueScheduleCreate {ty}`、`LeagueMatch {index, round}`、
    `LeaguePlayoff {round}`、`LeaguePromotion`、`DrawingTournamentGroup {ty}`、`DrawingTournament {ty}`、
    `TournamentGroupMatch {index, round}`、`TournamentMatch {index, round}`、`MinorPatch` / `MajorPatch` / `SeasonPatch`。
  - 每年都一样。
- **对局长度**：每场比赛的 `need_win`（BO3 = 2，BO5 = 3），本地 mod series_length 就是改它做的 BO7。

## v0.0.1

- **名字**（`text/ui.i18n`，合进游戏的 `asset/base/text/ui`，简体、繁体、英文）：

  | 原来 | 现在 |
  |---|---|
  | 韩国、中国、欧洲、北美、南美、日本 | LCK、LPL、LEC、LCS、CBLOL、LJL |
  | 各赛区乙级 | LCK CL、LDL、ERL、NACL、CBLOL 学院、LJL 学院 |
  | 大师赛 | 季中冠军赛 MSI |
  | 冠军赛 | 全球总决赛 |
  | 东部 / 西部挑战者杯 | 洲际赛（东部 / 西部） |

  赛区名（`region`：韩国、中国……）不变。
- **只读探测**：游戏载入生涯后，第一次跑经营 tick 时写 `league_esports_probe.json`，在游戏 `log.log` 旁边。内容：
  - 记录数；
  - 比赛规则设置（`GameSetting`）；
  - 每年的全年日程；
  - 联赛 / 杯赛的定义和每一届；
  - 每届国际赛小组赛、淘汰赛，以及最新 12 届联赛常规赛、季后赛、升降级赛的几场比赛。

  探测什么都不改。下一版每年变赛制、变赛程，要靠它先看清这些记录的样子，以及改它们的哪些部分游戏能接受。
- **日志** `league_esports.log`：载入，`PROBE written to …`，以及赛季切换（`SEASON ROLLOVER`）的内容。

## 装

- 单独的 mod：`python -I addons/league_addons/assemble.py OUT --standalone league_esports --dll <league_esports.dll>`，
  得到的文件夹放进 `<游戏目录>\mods\league_esports`。
- 新的代码 mod，要在游戏的 MOD 菜单里手动启用，再重启游戏。
