# 吕布奉先的素材（Codex 交付）

来源：Codex 2026-11-20 的交付，本地仓库 `D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-lubu`
（BoDUD/TeamFightMange2-mod 的旧检出，远端已不在）分支 `codex/ragnarok-lubu-assets-v02` 的提交 `00d78f3`
（素材 0.2.1，修过黑边重影），也在 `<游戏>\outputs\ragnarok_lubu_assets_v02.zip`。

`codex_v02/`：

- `ragnarok_lubu_native#sheet.png` / `#anim.fanim`：角色 8 个动作 x 8 帧，每格 128 x 128，脚底点 (64, 116)。就是游戏里的高清帧，
  `tools/art/import_lubu.py` 把挥砍特效画进去、缩出 1 倍帧，`tools/art/ppu_hd.py --hero lubu` 写 hd_ / lo_。
- `ragnarok_lubu_fx_native#sheet.png` / `#anim.fanim`：8 种特效 x 8 帧，同样的格子。挥痕、横扫、突刺、天喰蓄力和斩击画进他自己的帧，
  火花、天喰冲击、碎盾放进 `ragnarok/effects/ragnarok_lubu_fx`。
- `asset_manifest_v02.json`：帧时长、特效锚点（从脚底量）、触发时刻、四张图标的 SHA256。
- `ragnarok_lubu_passive.png`：被动图标（用户确认的那张）。游戏只有三个技能图标位，被动写在普攻说明里，这张不装进游戏。

Codex 做的 4 倍高清图集（4096 x 4096）是原画逐像素放大 4 倍，像素一样，没有收进来。

技能图标三张（`ragnarok/icons/`）是用户确认的高清版，原样 256 x 256，哈希和清单一致。

音频（15 条原创音效、10 条官方日语原声）不进仓库：`python tools/kit/seed_lubu_audio.py` 从交付里复制到 `ragnarok/sound/sfx/`。

## 第一轮补画（2026-11-20，Codex 分支 `codex/ragnarok-lubu-req1`）

我们提的需求：`D:/TFM2-Workshop/lubu_packs/LUBU_REQ1_PROMPT.md`。

- 方天画戟：普攻第 4-6 帧、横扫第 5-6 帧里戟杆没了，重画成完整长戟、双手握杆。`codex_v02/ragnarok_lubu_native#sheet.png`
  换成补画后的（另外 59 帧逐像素相同，`#anim.fanim` 一个字节没变，帧时长不变；接入前逐帧核过）。
- 天喰斩波：`codex_req1/ragnarok_lubu_wave_native`，8 帧 132 x 40，画朝右、上下对称，0.05 秒一帧。挂在天喰那一刀的
  画面直线上（`tools/kit/build_lubu.py` 的 `r_wave`），1 倍，转向跟着斩的方向。
- 选人立绘：Codex 选定的原图（`raw/card_selected.png`，1157 x 1359）用 `tools/art/bp_illustrations.py` 裁成卡面，
  在 `ragnarok/banpick_illustrations/ragnarok_lubu.png`。

## 照动画第一季重画（2026-11-21，`rebuild/`）

Codex 照首季设定重画了全部 64 帧（紫色鳞纹、金色双翎、单侧月牙方天戟），两倍格子：一格 256，脚底点 (128, 232)，个子和
原来一样（PPU 3.88，特效 3.3）。

- `rebuild/codex/ragnarok_lubu_native`：Codex 交来的原样，不改。`CODEX_HANDOFF.md`、`checks.csv`（每帧戟的位置和角度）、
  `weapon_master.png`（那把戟，64 帧都是它原样转过去的）也是交付原样。
- `rebuild/ragnarok_lubu_native`：`tools/art/lubu_rebuild_fix.py` 从上面那张做出来的：Codex 每帧的脸都单独画、大小不一，
  跑起来脸在变形，整套只用跑步第 1 帧的头（倒地低头的几帧用同一个头转过去）。
- `rebuild/ragnarok_lubu_fx_native`：特效图，`tools/art/lubu_fx.py` 照 Codex 的原画（游戏目录下 Codex 的检出，只读）按两倍重出。

顺序：`python tools/art/lubu_rebuild_fix.py`、`python tools/art/import_lubu.py`、`python tools/art/ppu_hd.py --hero lubu`、
`python tools/art/hero_reels.py --hero lubu`。烤进身体的特效位置按新画的帧量过（`import_lubu.py` 的 `BAKE`）。
