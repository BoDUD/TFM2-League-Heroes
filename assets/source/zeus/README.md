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
