# 维迦法强常驻附加包（测试版 v0.1.0）

用户：「顺便帮小法做一个 永久叠法强的」。主包 `league` 保持纯数据：维迦的被动「超凡邪力」每一层是他身上一个永久的
`league_veigar_p_stack`（法术强度 +1，击杀英雄那一层 +5）。引擎在他死亡时清掉身上全部 buff，数据也没有「复活时」这个时机，
所以主包里法强每条命从零叠起（说明里写着「死亡时清空」）。英雄联盟里维迦叠的法强是永久的。

这个附加包把主包的维迦换成 `override/` 里的副本（`make_override.py` 生成：技能一字不改，只加被动 `league_veigar_power:keep`，
普攻说明里的「死亡时清空」换成「【扩展包】死后保留」），被动每 tick 看一次：

- 活着时把身上每一层 `league_veigar_p_stack` 原样记下来（记在被动里，被动在玩家身上，死了不丢）；
- 身上比记下的少了（死亡或复活时引擎清掉）就把缺的层原样补回，死着的时候也补，倒下时数值不掉。

层数只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。

只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_veigar_power.log`
（`DEAD` / `ALIVE` 带记下的层数，`KEEP` 补回了几层、死着还是活着）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.88 以上）要装着并启用。
2. 把整个 `league_veigar_power` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_veigar_power.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看维迦普攻（被动）的说明：结尾是「【扩展包】死后保留」就说明换上了。

## 开发

```bash
python addons/league_veigar_power/make_override.py      # 主包的维迦或他的说明改了就重跑
cd addons && cargo test --release -p league_veigar_power && cargo build --release -p league_veigar_power
```
