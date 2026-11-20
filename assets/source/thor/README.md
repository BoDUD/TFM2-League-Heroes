# 索尔的素材（Codex 交付）

来源：Codex 2026-11-20 的交付，本地仓库 `D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-thor`
（BoDUD/TeamFightMange2-mod 的旧检出，远端已不在）分支 `codex/ragnarok-thor-assets-v01` 的提交 `6f4833f`（素材 0.1.2，
修过脸和跑步的腿、手臂）。交接说明在那边的 `docs/ragnarok_thor/CLAUDE_HANDOFF.md`。

`codex_v01/`：

- `ragnarok_thor_native#sheet.png` / `#anim.fanim`：角色 8 个动作 x 8 帧，每格 128 x 128，脚底点 (64, 116)。就是游戏里的高清帧，
  `tools/art/import_thor.py` 把挥锤、砸地雷电、大招蓄力和落锤画进去、切出投锤的空手和接锤、缩出 1 倍帧，
  `tools/art/ppu_hd.py --hero thor` 写 hd_ / lo_。待机整体比跑步、攻击往前偏 7 格，导入时整体挪回去（`SHIFT`，不重画）。
- `ragnarok_thor_fx_native#sheet.png` / `#anim.fanim`：8 种特效 x 8 帧，同样的格子。雷击、大招落地冲击、雷槌觉醒放进
  `ragnarok/effects/ragnarok_thor_fx`，飞行的雷槌放进 `ragnarok/effects/ragnarok_thor_proj`（1 倍，弹道画面）。
- `asset_manifest_v01.json`：帧时长、特效锚点（从脚底量）、触发时刻、四张图标的 SHA256。
- `ragnarok_thor_passive.png`：被动图标。游戏只有三个技能图标位，被动写在普攻说明里，这张不装进游戏。

技能图标三张（`ragnarok/icons/`）是 Codex 新画的 256 x 256，用户还没确认（清单里写的 `new_thor_draft`）。

音频（16 条原创音效、10 条官方日语原声）不进仓库：`python tools/kit/seed_thor_audio.py` 从交付里复制到 `ragnarok/sound/sfx/`。

## 第一轮补画（2026-11-20，Codex 分支 `codex/ragnarok-thor-req1`，`D:/TFM2-Workshop/thor_packs/THOR_REQ1_PROMPT.md`）

- 雷槌：普攻第 4-7 帧、技能第 4-7 帧、大招 8 帧、死亡第 4-8 帧（21 格）换成和待机一样大的同一把锤子（锤头 61 x 20 的模板，
  每帧只转角度、平移；死亡帧人往左挪 8 格放下整把锤子）。另外 43 格逐像素相同，`#anim.fanim` 一个字节没变，色板还是 40 色。
  我们接入时补了 32 个像素：死亡第 8 帧头发下面被擦成方口子的 27 格（从原画往左挪 8 格的同一位置拿回来），普攻第 4 帧拳头里 3 格、
  第 5 帧 1 格、大招第 2 帧小臂上 1 格的透明小洞（描边色、皮肤色）。这一轮的图后来被第二轮整张换掉。
- 选人立绘：Codex 没扩边的原图（`raw/generated_original.png`，1145 x 1374）用 `tools/art/bp_illustrations.py` 裁成卡面，
  在 `ragnarok/banpick_illustrations/ragnarok_thor.png`。

## 第二轮补画（2026-11-20，Codex 分支 `codex/ragnarok-thor-req2`，`D:/TFM2-Workshop/thor_packs/THOR_REQ2_PROMPT.md`）

- 人物大小统一（用户：「人物放技能的时候别一大一小啊」）：普攻、技能、投锤、大招、受击、死亡的 48 格从 Codex 的高分辨率原画按
  统一比例重新缩（普攻 x1.15-1.17、技能 x1.18、投锤 x1.04-1.09、大招和受击 x1.075、死亡 x1.08 左右），再把同一把雷槌（61 x 20 的
  锤头模板，大小不变）装回手上；待机、跑步 16 格逐像素不变，`#anim.fanim` 一个字节没变，还是 40 色。核对：和待机姿势相近的帧，
  待机按脚底缩放去套整身，比例 1.00-1.04，站直时头顶离脚底 52-56 格（待机 55）。
- 我们接入时又补了 8 个像素：普攻第 5 帧拳头和锤柄之间 4 格、技能第 5 帧两条小臂之间 2 格、大招第 5 帧描边断开的 2 格（周围 8 格里
  最多的颜色）。别的被包住的透明空隙两边都有描边，是手臂和身体、手臂和锤子之间本来的缝（待机原画里也有），不动。
  `codex_v01/ragnarok_thor_native#sheet.png` 现在就是第二轮这张加上这 8 格。
- 人变大以后画进帧里的特效跟着挪（`tools/art/import_thor.py` BAKE）：挥锤弧光 (24, -40) -> (27, -46)，砸地雷电 (35, 0) -> (28, 0)
  （对着锤头前半段和技能的判定区），大招蓄力 (-15, -72) -> (-16, -77)；大招落雷还落在地上的锤头上，不动。
