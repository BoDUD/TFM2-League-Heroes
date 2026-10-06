# 附加包合集（league_addons）

用户：「那还是做成一个附加包合集」。主包 `league` 保持纯数据（Windows、Mac、Linux 都能玩）；所有用原生代码做的附加包放进这一个 mod，
玩家只多订阅一个。合集里：魔腾全图黑暗、青钢影钩墙、基兰真回溯、李青 W 位移、剑魔锁链、凯隐变身、蛮王残血开大、赵信大招远程免伤、派克精确斩杀、卡兹克视野被动与按等级进化。

## 怎么合在一起

- 游戏一个 mod 只加载一个 DLL（`<mod_id>.dll`），所以不能把几个附加包的 DLL 放进同一个文件夹。这里把各附加包的源码当模块编进
  `league_addons.dll`（`src/lib.rs` 的 `#[path]`），每个附加包的 `register` 把自己的原生效果、被动、AI 钩子和地图读取注册进同一个
  `StableMod`。SDK 里这些都是列表（地图读取只有一个，只有钩墙用），名字只是约定加前缀，所以名字照旧（`league_nocturne_dark:start`
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
