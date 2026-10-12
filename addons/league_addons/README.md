# 附加包合集（league_addons）

用户：「那还是做成一个附加包合集」。主包 `league` 的英雄保持纯数据（主包 0.97.0 起自带的 `league.dll` 只管高清帧，源码在 `addons/league_main`，不进这个合集）；所有用原生代码做的附加包放进这一个 mod，
玩家只多订阅一个。合集里：魔腾全图黑暗、青钢影钩墙、基兰真回溯、李青 W 位移、剑魔锁链、凯隐变身、蛮王残血开大、赵信大招远程免伤、派克精确斩杀、卡兹克视野被动与按等级进化、格温被动的百分比最大生命值魔法伤害、布兰德被动的层数按每个敌人记、雷克顿低于一半生命时怒气积攒 +50%、凯尔的升阶和翅膀死后不掉、弗拉基米尔残血自动开血池、雷恩加尔站进地图草丛就能飞扑、劫的灭魂劫读真实生命和死亡印记按真实伤害结算、泰隆的刺客之道翻过地图的墙、赛娜的黑雾和维迦的法强死后不掉、辛德拉的 W 能举起小兵和野怪（大小龙除外）、佛耶戈附身（整个身体变成被附身的英雄）、泽丽的墙上激光和偷护盾、诺提勒斯的 Q 钩墙（锚撞到墙把自己拉过去、返还一半冷却）、诺手的大招读血（只在一刀砍得死人或诺克萨斯之力期间放）、古拉加斯的大招智能落点（酒桶落在敌人身后、把最多的人炸过来）、艾瑞莉娅的 Q 按真实印记和击杀刷新（还会借小兵跳向英雄）、卡萨丁的虚空之石正好减 10% 魔法伤害、能量脉冲按身边每次施法充能、虚空行走挑落点（能杀的、后排、不进塔下）。

## 怎么合在一起

- 游戏一个 mod 只加载一个 DLL（`<mod_id>.dll`），所以不能把几个附加包的 DLL 放进同一个文件夹。这里把各附加包的源码当模块编进
  `league_addons.dll`（`src/lib.rs` 的 `#[path]`），每个附加包的 `register` 把自己的原生效果、被动、AI 钩子和地图读取注册进同一个
  `StableMod`。SDK 里这些都是列表（地图读取只有一个：合集的 `MapReaders` 先调卡密尔的读墙、再调雷恩加尔的读草丛），名字只是约定加前缀，所以名字照旧（`league_nocturne_dark:start`
  等），各附加包的英雄数据原样可用。
- `build.rs` 打开 `league_bundle`：各附加包源码里的 `declare_stable_mod!` 只在单独编译时生效，合集只导出自己的入口。
  单独编译每个附加包还是它自己的 DLL（`cargo build --release` 一次全编）。
- 数据由 `assemble.py` 合成：复制各附加包的 `override/`、`effects/`，里面和 `mod.override_info` 里的 `asset/<附加包>/` 改成
  `asset/league_addons/`；文字合并成一个 `text/champion.i18n`（键是各附加包自己的 id，如 `description.league_leesin_hop`，不会撞）；
  `mod.mod_info` 要求的主包版本取各附加包里最高的。
- 合集和单独的附加包不能同时启用：两边替换同一个英雄、注册同名的原生效果。

## 生成和测试

```bash
cd addons && cargo build --release                      # 得到 target/release/league_addons.dll（和各附加包自己的 DLL）
python addons/league_addons/assemble.py <输出文件夹>       # 全部附加包；--only league_nocturne_dark,league_leesin_hop 只放已发布英雄的
```

把输出文件夹改名 `league_addons` 放进 `<游戏目录>\mods\`（先关掉单独的附加包），在 MOD 菜单里启用并排在主包后面，重启游戏。
各附加包的日志照旧各写各的（`%APPDATA%\TeamSamoyed\TeamfightManager2\data\<附加包>.log`），合集启动时每个附加包各记一行「loaded」。
