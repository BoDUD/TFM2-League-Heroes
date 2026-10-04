# 魔腾黑暗附加包（测试版 v0.3.0）

主包 `league` 保持纯数据。主包里魔腾的 R 让己方所有英雄隐身 3 秒、敌方英雄头上一团黑雾，再飞扑一名敌方英雄。
这个附加包用原生代码把「黑暗降临」做得更像 League：

- **敌人只能看见身边**：R 期间（180 tick），魔腾一方的每个英雄，40000 内没有敌方英雄时隐身（每 tick 续上），
  有敌方英雄贴近就现身。League 里被黑暗笼罩的人视野缩到身边；本作没有按队伍改视野的接口，用「贴近才看得见」来做。
- **全地图变暗**：R 出手时，在地图中心播一张盖满整张地图（1280×1280，含四周边框）的半透明深蓝贴图，
  叠 3 层、每层隔 4 tick，各播 3 秒，所以很快地一层层变暗、最后一层层亮回来（约 55% 暗）。
  它画在单位下面（z −2）：地面变暗，英雄、血条和技能特效照样看得清。
- **敌人只打得到身边的（v0.3.0，鬼影重重）**：本作的视野是全队共享的——一个敌人贴近，整队都看得见，魔腾飞扑落地后
  连远处的射手都锁他（测试时 R 期间 52 次出手里 47 次打魔腾，一半从 6 万外起手）。League 的鬼影重重是每个敌人只看得见
  自己身边、没有共享视野。所以黑暗里每个敌方英雄每 tick 的决定都过一遍（扩展包的「玩家 AI 输入」钩子）：他要攻击、
  施放到的魔腾一方单位（英雄、小兵）离他超过 40000，这一下就换成朝它走过去，走到 40000 以内照常出手。指向点的技能看
  点附近 15000 内的单位，指方向的看方向两侧 15 度、150000 内离方向线最近的。近战基本不受影响，远程和远距离技能要贴近才打得到。
- 黑雾、飞扑、伤害、画面、声音都和主包一样。

暗色是普通的特效事件：在模拟里随 R 播放，跟比赛画面一起录下、一起回放，和英雄的动作同步。
v0.1.x 用客户端每帧叠一层暗色、跟着模拟里「黑暗还在」的记录走；可游戏先在后台把比赛算到前面去，再按正常速度播给你看，
暗色就和画面对不上（没开 R 也一闪一闪地黑）——v0.2.0 去掉了这套，不再注册客户端扩展。

## 在游戏里测

1. 主包（League of Legends Heroes 0.50 以上）要装着并启用。
2. 把整个 `league_nocturne_dark` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_nocturne_dark.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`、`effects\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看魔腾 R 的说明：开头是「【黑暗测试版】」就说明替换成功。
5. 打几局有魔腾的对局，看他放 R 时地图有没有变暗、没放 R 时是不是一直正常，他的队友是不是离敌人远时看不见。
6. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nocturne_dark.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   `DARKNESS for 180 ticks: 3 of 5 allies unseen`（R 出手时几个队友隐身）、`darkness over`（黑暗结束）、
   `PARANOIA: player 7 Attack out of sight (87000 away) - walks there instead`（某个敌人想隔空出手被拦下，同一人每 30 tick 记一行）。

## 开发

- `python addons/league_nocturne_dark/make_override.py`：从主包重新生成 `override/`、`text/` 和 `effects/`（去掉 R 的全体隐身，
  调 `league_nocturne_dark:start`，加暗色特效 `league_nocturne_dark_veil` 和它的贴图）。主包的魔腾改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_nocturne_dark`：单元测试和 `tests/wiring.rs`（迷你模拟）。
- 在 `addons/` 下 `cargo build --release -p league_nocturne_dark`（Windows）得到 `target/release/league_nocturne_dark.dll`。
