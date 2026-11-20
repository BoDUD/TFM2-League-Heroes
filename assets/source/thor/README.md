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

## 待补（第一轮补画，`D:/TFM2-Workshop/thor_packs/THOR_REQ1_PROMPT.md`）

- 雷槌：普攻第 4-7 帧、技能第 4-7 帧、死亡第 4-8 帧里锤头只有待机的一半长，大招 8 帧换成了另一把短方锤（必须改）。
- 选人立绘：A 手绘风格，和别的英雄一样。
