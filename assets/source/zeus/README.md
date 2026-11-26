# 宙斯的素材（Codex 交付）

来源：Codex 2026-11-21 的交付，本地仓库 `D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-zeus`
（BoDUD/TeamFightMange2-mod 的旧检出，远端已不在）分支 `codex/ragnarok-zeus-assets` 的提交 `de2b95f`。交接说明在那边的
`docs/ragnarok_zeus/CLAUDE_HANDOFF.md`。

一个英雄、三种身体：老人（elder）、肌肉膨胀（muscle）、阿陀磨须（adamas），加上三段变身过程。

`codex_v01/`：

- `ragnarok_zeus_elder_native`、`_muscle_native`、`_adamas_native`（`#sheet.png` / `#anim.fanim`）：三种身体各一张，idle、run、
  attack、skill、hit、dead 各 8 帧，skill2 4 帧，每格 128 x 128，脚底点 (64, 116)。头顶离脚底：老人 51 格、膨胀 67 格、
  阿陀磨须 59 格（每种身体内各动作一样大，核对过：套待机的比例 0.94-1.04）。
- `ragnarok_zeus_transform_native`：expand（老人 -> 膨胀 1.02 秒）、compress（膨胀 -> 阿陀磨须 1.04 秒）、revert（阿陀磨须
  -> 老人 0.93 秒），每段 8 帧，首尾帧和两种身体的待机第一帧逐像素相同。
- `ragnarok_zeus_fx_native`：8 种特效 x 8 帧。拳风、连拳的气流、超越时间之拳的蓄力和打出、变身的光画进他自己的帧，
  拳光、连拳的雷光、变身完成的脚下一圈放进 `ragnarok/effects/ragnarok_zeus_fx`。
- `asset_manifest.json`：每张图的帧数、时长、采样比例、色板。
- `ragnarok_zeus_passive.png`：被动图标。游戏只有三个技能图标位，被动写在普攻说明里，这张不装进游戏。

`tools/art/import_zeus.py` 把五张图合成一张（老人的标签原样、膨胀 mu_*、阿陀磨须 ad_*、expand、大招 `ult` 就是 compress、
revert），缩出 1 倍帧；`tools/art/ppu_hd.py --hero zeus` 写 hd_ / lo_，`tools/art/hero_reels.py --hero zeus` 写三种身体
各自的待机动图（idle、mu_idle、ad_idle）和选人动图。站着、跑着、出手、挨打、倒下按形态换哪套帧由 ragnarok.dll 的显示钩子做
（`addons/ragnarok/src/zeus.rs`）。

技能图标三张（`ragnarok/icons/`）是 Codex 画的 256 x 256。选人立绘：Codex 没扩边的原图（`design/ragnarok_zeus/art/source/v2/
v2_card.png`，1145 x 1374）用 `tools/art/bp_illustrations.py` 裁成卡面，在 `ragnarok/banpick_illustrations/ragnarok_zeus.png`。

音频（16 条原创音效、6 条官方日语原声，宣传口号那句只放演示页）不进仓库：`python tools/kit/seed_zeus_audio.py`
从交付里复制到 `ragnarok/sound/sfx/`。

接入时检查过：三种身体各动作大小一致、过渡首尾接得上、没有碎点和贴边。被包住的透明小缝都在手臂和身体、手臂之间，
两边有描边，是本来的画法。

## 两倍密度重出（2026-11-21）

用户看过亚当的两倍版以后：「然后调整另外三个 全都在一个pr里处理就行」。`repixel/` 是 `tools/art/zeus_repixel.py` 照
Codex 的原画按两倍密度重出的五张图（一格 256，脚底点 (128, 232)，位置、缩放照 Codex 的 build_assets.py 每帧记下来再乘 2），
游戏里 PPU 3.3，个子不变；`tools/art/import_zeus.py` 现在从这里读。`codex_v01/` 留着当原样的参照。

- 颜色还是 Codex 定的 22 色（只把白袍、头发阴影里被换成皮肤色的冷灰改回白），描边用同色系最深的那档，不是一圈近黑。
- 眼睛的金色占到一点就留成金点（Codex 的 128 格里多半丢了）。
- 时间之拳打出那帧的拳头、膨胀普攻第 5 帧的拳头、倒地最后几帧的脚：Codex 按格子切原画时切掉了，接了回来（位置、大小不动）。
- 变身三段的头尾两帧还是两种身体待机的第一帧，切换时接得上。
- 待机动图（`tools/art/hero_reels.json`）三种身体都指定了帧：自动挑会挑到变身发光的帧、连拳气流的尾巴。
- 原画不在仓库里，在游戏目录下 Codex 的检出（de2b95f），脚本只读它（环境变量 `ZEUS_CODEX` 可以改路径）。
